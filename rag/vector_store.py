import os
from langchain_chroma import Chroma
from model.factory import get_embedding_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from utils.config_handler import chroma_conf
from utils.path_tool import get_abs_path
from utils.file_handler import pdf_loader, txt_loader, listdir_with_allowed_type, get_file_md5_hex
from utils.logger_handler import logger

class VectorStoreService:
    def __init__(self):
        self.persist_directory = get_abs_path(chroma_conf["persist_directory"])
        self.md5_store_path = get_abs_path(chroma_conf["md5_hex_store"])
        self.data_path = get_abs_path(chroma_conf["data_path"])
        self.vector_store = Chroma(
            collection_name=chroma_conf["collection_name"],
            embedding_function=get_embedding_model(),
            persist_directory=self.persist_directory
        )
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf["chunk_size"],
            chunk_overlap=chroma_conf["chunk_overlap"],
            separators=chroma_conf["separators"],
            length_function=len,
        )

    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_conf["k"]})

    def is_vector_store_empty(self) -> bool:
        try:
            return self.vector_store._collection.count() == 0
        except Exception as e:
            logger.warning(f"[加载知识库]检查向量库数量失败，将尝试重新加载：{str(e)}")
            return True

    def ensure_loaded(self):
        if (
            not os.path.exists(self.persist_directory)
            or not os.path.exists(self.md5_store_path)
            or self.is_vector_store_empty()
        ):
            logger.info("[加载知识库]检测到本地向量库缺失、为空或MD5记录缺失，开始初始化知识库")
            self.load_documents()

    def load_documents(self):
        def check_md5_hex(md5_for_check: str):
            if not md5_for_check:
                return False
            if not os.path.exists(self.md5_store_path):
                open(self.md5_store_path, "w", encoding="utf-8").close()
                return False
            with open(self.md5_store_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line == md5_for_check:
                        return True
                return False

        def save_md5_hex(md5_for_save: str):
            with open(self.md5_store_path, "a", encoding="utf-8") as f:
                f.write(md5_for_save + "\n")

        def get_file_documents(read_path: str):
            if read_path.endswith(".pdf"):
                return pdf_loader(read_path)
            if read_path.endswith(".txt"):
                return txt_loader(read_path)
            return []

        allowed_files_path: list[str] = listdir_with_allowed_type(
            self.data_path,
            tuple(chroma_conf["allow_knowledge_file_types"])
        )
        for file_path in allowed_files_path:
            # 获取文件md5
            md5_hex = get_file_md5_hex(file_path)
            if check_md5_hex(md5_hex):
                logger.info(f"[加载知识库]文件已存在知识库当中：{file_path}")
                continue
            try:
                # 加载文件内容
                documents: list[Document] = get_file_documents(file_path)
                if not documents:
                    logger.warning(f"[加载知识库]文件内无有效文本内容：{file_path}")
                    continue
                # 对文件进行分片
                split_documents: list[Document] = self.spliter.split_documents(documents)
                if not split_documents:
                    logger.warning(f"[加载知识库]分片后无有效文本内容：{file_path}")
                    continue
                # 将内容存入向量库
                self.vector_store.add_documents(split_documents)
                # 记录md5值，避免重复加入
                save_md5_hex(md5_hex)

                logger.info(f"[加载知识库]文件加入成功：{file_path}")
            except Exception as e:
                logger.error(f"[加载知识库]文件加入失败：{file_path}。{str(e)}", exc_info=True)
                continue
