from abc import ABC, abstractmethod
from typing import Optional
from langchain_core.embeddings import Embeddings
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.chat_models.tongyi import ChatTongyi, BaseChatModel
from utils.config_handler import rag_conf

def get_api_key() -> str:
    api_key = rag_conf.get("api_key", "")
    if not api_key or api_key.startswith("${"):
        raise RuntimeError(
            "未配置 DASHSCOPE_API_KEY。请先设置环境变量 DASHSCOPE_API_KEY，"
            "或在 .env/系统环境中提供有效密钥后重新启动应用。"
        )
    return api_key


class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass

class ChatModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return ChatTongyi(api_key=get_api_key(), model=rag_conf["chat_model_name"])

class EmbeddingModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return DashScopeEmbeddings(dashscope_api_key=get_api_key(), model=rag_conf["embedding_model_name"])

def get_chat_model():
    return ChatModelFactory().generator()


def get_embedding_model():
    return EmbeddingModelFactory().generator()
