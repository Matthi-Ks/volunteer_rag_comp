from abc import ABC, abstractmethod

from models.query import Query


class RagBase(ABC):
    def __init__(self, client, vectorStore, kg_store, llmService, rerankService):
        self.client = client
        self.vectorStore = vectorStore
        self.kg_store = kg_store
        self.rerankService = rerankService
        self.llmService = llmService


    @abstractmethod
    def execute_pipeline(self, query: Query):
        pass

    # strip input text of unwanted symbols and formating
    def __query_preprocessing(self, query: str) -> str:
        query = "".join(query.lower().strip().split())
        return query
