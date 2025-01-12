# tests/test_integration/test_real_translation.py
import logging
import pytest
from fastapi.testclient import TestClient
from main import app
from app.core.config import get_settings
from app.services.cache import TranslationCache

logger = logging.getLogger(__name__)
settings = get_settings()


@pytest.fixture(autouse=True)
def clear_cache():
    """每次测试前自动清理缓存"""
    cache = TranslationCache()
    cache.clear()


@pytest.mark.skipif(not settings.API_KEY, reason="API key not configured")
def test_real_translation():
    """测试实际的翻译功能"""
    client = TestClient(app)
    
    logger.info("\n=== Configuration ===")
    logger.info(f"API Key configured: {'Yes' if settings.API_KEY else 'No'}")
    logger.info(f"API Key: {settings.API_KEY[:15]}...")
    
    test_cases = [
        {
            "text": "Hello, this is a test message.",
            "expected_keywords": ["你好", "测试"]
        }
    ]
    
    for case in test_cases:
        try:
            logger.info("\n=== Test Case ===")
            logger.info(f"Input: {case['text']}")
            
            response = client.post(
                "/translate",
                json={
                    "text": case["text"],
                    "from_lang": "en",
                    "to_lang": "zh"
                }
            )
            
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Response Headers: {dict(response.headers)}")
            
            data = response.json()
            logger.info(f"Response Body: {data}")
            
            if 'error' in data:
                logger.error(f"API Error: {data['error']}")
            
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            assert "translated_text" in data, "No translated_text in response"
            assert data["translated_text"] != case["text"], "Translation returned original text"
            
            # 验证翻译结果
            translated = data["translated_text"]
            logger.info(f"Translated text: {translated}")
            
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            logger.exception("Full traceback:")
            raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pytest.main(["-sv", __file__])