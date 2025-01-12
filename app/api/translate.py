# translate.py API 路由

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.translator import TranslationService
from ..services.cache import TranslationCache

import logging
from fastapi import Request, Depends

logger = logging.getLogger(__name__)
router = APIRouter()
# translation_service = TranslationService()
cache_service = TranslationCache()

from main import translation_service

class TranslateRequest(BaseModel):
    text: str
    from_lang: str = "en"
    to_lang: str = "zh"

def get_translation_service(request: Request) -> TranslationService:
    return request.app.state.translation_service

@router.post("/translate")
async def translate_text(request: TranslateRequest, service: TranslationService = Depends(get_translation_service)):
    logger.info(f"Received translation request for text: {request.text[:50]}...")
    try:
        # 先检查缓存
        cached = cache_service.get(request.text)
        if cached:
            logger.info("Found in cache")
            return {"translated_text": cached}
        
        logger.info("Calling translation service...")
        logger.info(f"Request text: {request.text}")
        translated = await service.translate_chunks(request.text)
        logger.info(f"Translation completed: {translated[:50]}...")
        
        # 保存到缓存
        cache_service.set(request.text, translated)
        
        return {"translated_text": translated}
    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        logger.exception("Full traceback:")
        # 错误时返回400而不是200
        raise HTTPException(status_code=400, detail=str(e))