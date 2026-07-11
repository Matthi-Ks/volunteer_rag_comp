from abc import ABC, abstractmethod

from models.pipeline_result import PipelineResult
from models.query import Query


class RagBase(ABC):
    def __init__(self, vectorStore, kg_store, llmService, rerankService):
        self.vectorStore = vectorStore
        self.kg_store = kg_store
        self.rerankService = rerankService
        self.llmService = llmService

    # takes a query object and generates an answer for each question variant
    @abstractmethod
    def execute_pipeline(self, query: Query) -> list[PipelineResult]:
        pass

