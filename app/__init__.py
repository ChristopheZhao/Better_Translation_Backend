# app/__init__.py
import logging
from openai import AsyncOpenAI
from .core.config import get_settings

logger = logging.getLogger(__name__)

async def verify_api_key():
    """验证 API key 是否有效"""
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.API_KEY)
    try:
        # 尝试一个简单的API调用
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1
        )
        logger.info("API key verified successfully")
        return True
    except Exception as e:
        logger.error(f"API key verification failed: {str(e)}")
        return False