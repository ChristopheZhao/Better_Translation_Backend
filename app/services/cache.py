import json
from pathlib import Path
from hashlib import md5
from ..core.config import get_settings

settings = get_settings()

class TranslationCache:
    def __init__(self):
        self.cache_dir = Path(settings.CACHE_DIR)
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_key(self, text: str) -> str:
        return md5(text.encode()).hexdigest()
    
    def get(self, text: str) -> str | None:
        if not settings.CACHE_ENABLED:
            return None
            
        cache_key = self._get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            with cache_file.open('r', encoding='utf-8') as f:
                return json.load(f)['translation']
        return None
    
    def set(self, text: str, translation: str):
        if not settings.CACHE_ENABLED:
            return
            
        cache_key = self._get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        with cache_file.open('w', encoding='utf-8') as f:
            json.dump({
                'original': text,
                'translation': translation
            }, f, ensure_ascii=False, indent=2)

    def clear(self):
        """清除所有缓存文件"""
        for cache_file in self.cache_dir.glob('*.json'):
            cache_file.unlink()