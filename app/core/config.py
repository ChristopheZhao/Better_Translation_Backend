from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # 应用基础配置
    APP_NAME: str = "Better Translator"
    LOG_LEVEL: str = "INFO"

    # 缓存配置
    CACHE_ENABLED: bool = True
    CACHE_DIR: str = "./cache"

    # OpenAI配置
    API_KEY: str = ""

    # 文心配置
    ERNIE_API_KEY: str = ""
    ERNIE_SECRET_KEY: str = ""
    ERNIE_API_URL: str = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions"

    # 选择使用哪个翻译服务："openai" 或 "ernie"
    TRANSLATOR_TYPE: str = "openai"
    
    model_config = ConfigDict(
        env_file='.env',
        case_sensitive=True
    )
    
    model_config = ConfigDict(
        env_file='.env',
        case_sensitive=True
    )

@lru_cache()
def get_settings():
    return Settings()