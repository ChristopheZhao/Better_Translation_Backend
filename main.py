from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import translate
from app.core.config import get_settings

import logging
from dotenv import load_dotenv
from app.services.translator import TranslationService
import os


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
load_dotenv()

logger.info(f"Environment loaded. API_KEY present: {'API_KEY' in os.environ}")

settings = get_settings()

app = FastAPI(title=settings.APP_NAME)

# 添加 CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有域
    allow_credentials=False,  # 必须设为 False，因为 allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(translate.router)

# 全局 TranslationService 实例
translation_service = None

@app.on_event("startup")
async def startup_event():
    global translation_service
    translation_service = TranslationService()
    await translation_service.initialize()
    app.state.translation_service = translation_service
    logger.info("TranslationService initialized.")

@app.on_event("shutdown")
async def shutdown_event():
    if translation_service:
        await translation_service.close()
        logger.info("TranslationService shut down.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)