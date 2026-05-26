from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompt
from model.factory import chat_model

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

class RagSummarizeService(object):
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.retriever = self.vector_store.get_retriever()
        self.prompt_text = load_rag_prompt()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = chat_model
        self.chain = self._init_chain()

    def _init_chain(self):
        chain = self.prompt_template | self.model | StrOutputParser()
        return  chain

    def retrieve(self, query: str) -> list[Document]:
        docs = self.retriever.invoke(query)
        return docs

    def rag_summarize(self, query: str) -> str:
        docs = self.retrieve(query)
        context = ""
        counter = 0
        for doc in docs:
            counter += 1
            context += f"【参考资料{counter}】：参考资料：{doc.page_content} | 参考元数据：{doc.metadata}\n"
        return self.chain.invoke({"input": query, "context": context})

if __name__ == "__main__":
    rag = RagSummarizeService()
    print(rag.rag_summarize("大户型适合什么扫地机器人"))
