from typing import List
import re
import logging
import aiohttp
import asyncio
from abc import ABC, abstractmethod
from openai import AsyncOpenAI
from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

PLACEHOLDER = "<<PARAGRAPH_BREAK>>"

class BaseTranslator(ABC):
    @abstractmethod
    async def translate(self, text: str) -> str:
        pass

    def replace_paragraph_breaks(self, text: str) -> str:
        """
        用占位符替换段落分隔符
        """
        return text.replace('\n\n', PLACEHOLDER)

    def restore_paragraph_breaks(self, text: str) -> str:
        """
        将占位符替换回段落分隔符
        """
        return text.replace(PLACEHOLDER, '\n\n')

class OpenAITranslator(BaseTranslator):
    def __init__(self, api_key: str):
        self.openai_client = AsyncOpenAI(api_key=api_key)

    async def translate(self, text: str) -> str:
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a professional translator. "
                            "Translate the following English text to Simplified Chinese while preserving the original formatting, including paragraphs and line breaks."
                        )
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ]
            )
            translated_text = response.choices[0].message.content
            # 统一换行符
            translated_text = translated_text.replace('\r\n', '\n')
            logger.debug(f"OpenAI Translated text: {translated_text}")
            return translated_text
        except Exception as e:
            logger.error(f"OpenAI translation error: {str(e)}")
            raise

class ErnieTranslator(BaseTranslator):
    def __init__(self, api_key: str, secret_key: str, api_url: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.api_url = api_url
        self.access_token = None
        self.session = None

    async def initialize_session(self):
        self.session = aiohttp.ClientSession()

    async def get_access_token(self) -> str:
        if self.access_token:
            return self.access_token

        token_url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }

        try:
            async with self.session.post(token_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    self.access_token = data.get("access_token")
                    if not self.access_token:
                        raise RuntimeError("Access token not found in response")
                    return self.access_token
                else:
                    error_text = await response.text()
                    raise RuntimeError(f"Failed to get access token: {error_text}")
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error while getting access token: {str(e)}")
            raise
        except asyncio.TimeoutError as e:
            logger.error(f"Timeout error while getting access token: {str(e)}")
            raise

    async def translate(self, text: str) -> str:
        try:
            access_token = await self.get_access_token()
            url = f"{self.api_url}?access_token={access_token}"

            payload = {
                "messages": [{
                    "role": "user",
                    "content": (
                        "Translate the following English text to Simplified Chinese while preserving the original formatting, including paragraphs and line breaks:\n\n"
                        f"{text}"
                    )
                }],
                "temperature": 0.7,
                "max_tokens": 2000,
                "penalty_score": 1.0,
                "enable_system_memory": False,
                "disable_search": True,
                "enable_citation": False,
                "enable_trace": False
            }

            headers = {
                'Content-Type': 'application/json'
            }

            async with self.session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    response_data = await response.text()
                    raise RuntimeError(f"Ernie API error: {response_data}")

                response_json = await response.json()
                logger.debug(f"Ernie API response: {response_json}")

                result = response_json.get("result")
                if not result:
                    raise RuntimeError("Ernie API response missing 'result' field")

                # 统一换行符
                result = result.replace('\r\n', '\n')

                logger.debug(f"Ernie Translated text: {result}")

                return result
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error during Ernie translation: {str(e)}")
            raise
        except asyncio.TimeoutError as e:
            logger.error(f"Timeout error during Ernie translation: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Ernie translation: {str(e)}")
            raise

    async def close(self):
        if self.session:
            await self.session.close()
            logger.info("Ernie session closed")

class TranslationService:
    def __init__(self):
        api_key = settings.API_KEY
        logger.info(f"TranslationService initialized with API key: {api_key[:8]}...")

        self.service_type = settings.TRANSLATOR_TYPE.lower()
        if self.service_type == "openai":
            self.translator = OpenAITranslator(api_key=api_key)
        elif self.service_type == "ernie":
            self.translator = ErnieTranslator(
                api_key=settings.ERNIE_API_KEY,
                secret_key=settings.ERNIE_SECRET_KEY,
                api_url="https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions"
            )
        else:
            raise ValueError(f"Unsupported translator type: {self.service_type}")

    def split_text_by_paragraphs(self, text: str) -> List[str]:
        """
        按段落分割文本，保留段落结构
        """
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]

    def split_text_by_sentences(self, text: str) -> List[str]:
        """
        按句子分割文本，保持语义完整性
        """
        sentence_ends = r'(?<=[.!?。！？])\s+'
        sentences = re.split(sentence_ends, text)
        return [s.strip() for s in sentences if s.strip()]

    def merge_chunks_by_size(self, paragraphs: List[str], chunk_size: int = 1000) -> List[str]:
        """
        将段落合并成适当大小的块，保持段落完整性
        """
        chunks = []
        current_chunk = []
        current_size = 0

        for paragraph in paragraphs:
            paragraph_size = len(paragraph)

            # 检查添加当前段落是否会超出chunk_size
            if current_size + paragraph_size + 2 > chunk_size and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_size = 0

            current_chunk.append(paragraph)
            current_size += paragraph_size + 2  # +2 for two newline characters

        # 添加最后一个chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))

        return chunks

    async def translate_text(self, text: str) -> str:
        """翻译文本"""
        try:
            return await self.translator.translate(text)
        except Exception as e:
            logger.error(f"Translation error ({self.service_type}): {str(e)}")
            raise

    async def translate_chunks(self, text: str, chunk_size: int = 1000, max_concurrent: int = 10) -> str:
        if len(text) <= chunk_size:
            translated = await self.translate_text(self.translator.replace_paragraph_breaks(text))
            return self.translator.restore_paragraph_breaks(translated)

        # 1. 按段落分割文本
        paragraphs = self.split_text_by_paragraphs(text)

        # 2. 将段落合并成适当大小的块
        chunks = self.merge_chunks_by_size(paragraphs, chunk_size)

        # 3. 使用占位符替换段落分隔符
        chunks_with_placeholders = [self.translator.replace_paragraph_breaks(chunk) for chunk in chunks]

        # 4. 翻译每个块
        semaphore = asyncio.Semaphore(max_concurrent)

        async def translate_with_semaphore(chunk):
            async with semaphore:
                return await self.translate_text(chunk)

        translated_chunks = await asyncio.gather(
            *[translate_with_semaphore(chunk) for chunk in chunks_with_placeholders],
            return_exceptions=True
        )

        # 5. 处理可能的异常并合并翻译结果
        final_translations = []
        for idx, result in enumerate(translated_chunks):
            if isinstance(result, Exception):
                logger.error(f"Error translating chunk {idx}: {str(result)}")
                final_translations.append(f"[Translation Error: {str(result)}]")
            else:
                # 恢复段落分隔符
                restored = self.translator.restore_paragraph_breaks(result)
                final_translations.append(restored)

        # 6. 合并所有翻译后的块
        return '\n\n'.join(final_translations)

    async def close(self):
        """关闭翻译服务，释放资源"""
        if isinstance(self.translator, ErnieTranslator):
            await self.translator.close()

    async def initialize(self):
        if isinstance(self.translator, ErnieTranslator):
            await self.translator.initialize_session()

# 使用示例
# async def main():
#     service = TranslationService()
#     text = (
#         "This is the first paragraph.\n\n"
#         "This is the second paragraph, which is a bit longer and might require chunking if it exceeds the chunk size limit.\n\n"
#         "This is the third paragraph."
#     )
#     translated_text = await service.translate_chunks(text)
#     print("Translated Text:")
#     print(translated_text)
#     await service.close()

# asyncio.run(main())
