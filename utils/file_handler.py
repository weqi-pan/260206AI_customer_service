import os, hashlib
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from utils.logger_handler import logger


# 获取文件md5的十六进制字符串
def get_file_md5_hex(filepath: str):
    if not os.path.exists(filepath):
        logger.error(f"[md5计算]文件不存在：{filepath}")
        return None
    if not os.path.isfile(filepath):
        logger.error(f"[md5计算]不是文件：{filepath}")
        return None
    md5_obj = hashlib.md5()
    chunk_size = 4096 # 分片大小为4KB，避免内存溢出
    try:
        with open(filepath, "rb") as f: # 二进制模式打开文件（计算md5必须是二进制模式）
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)
            md5_hex = md5_obj.hexdigest()
            return md5_hex
    except Exception as e:
        logger.error(f"[md5计算]文件计算md5失败：{filepath}")
        return None

# 获取文件列表（允许的文件后缀）
def listdir_with_allowed_type(path: str, allowed_type: tuple[str]):
    files = []
    if not os.path.isdir(path):
        logger.error(f"[文件列表]路径不是目录：{path}")
        return allowed_type

    for f in os.listdir(path):
        if f.endswith(allowed_type):
            files.append(os.path.join(path, f))

    return tuple(files)

# 加载PDF文档
def pdf_loader(filepath: str, password = None) -> list[Document]:
    return PyPDFLoader(filepath, password).load()

# 加载TXT文档
def txt_loader(filepath: str) -> list[Document]:
    return TextLoader(filepath, encoding="utf-8").load()