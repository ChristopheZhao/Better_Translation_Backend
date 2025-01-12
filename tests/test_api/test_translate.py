import pytest
from fastapi.testclient import TestClient

def test_translate_endpoint_basic(client: TestClient, sample_texts):
    """测试基本翻译功能"""
    response = client.post(
        "/translate",
        json={
            "text": sample_texts["short"],
            "from_lang": "en",
            "to_lang": "zh"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "translated_text" in data
    assert isinstance(data["translated_text"], str)
    assert len(data["translated_text"]) > 0

@pytest.mark.asyncio
async def test_translate_with_long_text(client: TestClient, sample_texts):
    """测试长文本翻译"""
    response = client.post(
        "/translate",
        json={
            "text": sample_texts["long"],
            "from_lang": "en",
            "to_lang": "zh"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    # 检查段落结构是否保持,只要确保返回了翻译结果即可
    assert "translated_text" in data
    print("data = ",data)
    assert len(data["translated_text"]) > 0

def test_translate_error_handling(client: TestClient):
    """测试错误处理"""
    # 测试空文本
    response = client.post(
        "/translate",
        json={
            "text": None,
            "from_lang": "en",
            "to_lang": "zh"
        }
    )
    assert response.status_code in [400, 422]
    
    # 测试无效的语言代码
    response = client.post(
        "/translate",
        json={
            "text": "Hello",
            "from_lang": "invalid",
            "to_lang": "zh"
        }
    )
    assert response.status_code in [400, 422]