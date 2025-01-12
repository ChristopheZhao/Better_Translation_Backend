import pytest
from app.services.translator import TranslationService

@pytest.fixture
def translator():
    return TranslationService()

@pytest.mark.asyncio
async def test_translate_text(translator: TranslationService):
    """测试基本翻译功能"""
    text = "Hello, world!"
    result = await translator.translate_text(text)
    assert result
    assert isinstance(result, str)
    assert len(result) > 0

@pytest.mark.asyncio
async def test_translate_chunks(translator: TranslationService, sample_texts):
    """测试文本分块翻译"""
    result = await translator.translate_chunks(sample_texts["medium"])
    assert result
    assert isinstance(result, str)
    
    # 检查分块是否正确
    chunks = translator.merge_chunks_by_size(
        translator.split_text_by_sentences(sample_texts["medium"])
    )
    assert all(len(chunk) <= 1000 for chunk in chunks)

def test_split_text_by_sentences(translator: TranslationService, sample_texts):
    """测试句子分割功能"""
    sentences = translator.split_text_by_sentences(sample_texts["medium"])
    assert len(sentences) >= 3
    for sentence in sentences:
        assert sentence.strip()
        assert translator.is_sentence_complete(sentence)