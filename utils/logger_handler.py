import logging
import os
from datetime import datetime

from utils.path_tool import get_abs_path

# 日志保存根目录
log_root = get_abs_path("logs")

# 确保日志目录存在
os.makedirs(log_root, exist_ok=True)

# 日志格式配置
default_log_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)

def get_logger(
        name: str = "agent",
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        log_file = None
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 避免重复添加Handler
    if logger.handlers:
        return logger

    # 控制台日志
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(default_log_format)

    logger.addHandler(console_handler)

    # 文件日志
    if not log_file:
        log_file = os.path.join(log_root, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(file_level)
    file_handler.setFormatter(default_log_format)

    logger.addHandler(file_handler)

    return  logger

# 快捷获取日志器
logger = get_logger()