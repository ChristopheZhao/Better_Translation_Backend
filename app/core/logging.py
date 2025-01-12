import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from ..core.config import get_settings

settings = get_settings()

def setup_logging():
    # 创建logs目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 配置日志格式
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建日志处理器
    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(log_format)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # 为主要组件创建日志记录器
    loggers = {
        'translator': logging.getLogger('translator'),
        'api': logging.getLogger('api'),
        'cache': logging.getLogger('cache')
    }
    
    for logger in loggers.values():
        logger.setLevel(settings.LOG_LEVEL)
    
    return loggers