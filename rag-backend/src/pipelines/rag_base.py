from abc import ABC, abstractmethod

from models.pipeline_result import PipelineResult
from models.query import Query


class RagBase(ABC):
    def __init__(self, vectorStore, kg_store):
        self.vectorStore = vectorStore
        self.kg_store = kg_store

    # takes a query object and generates an answer for each question variant
    @abstractmethod
    def execute_pipeline(self, query: Query) -> list[PipelineResult]:
        pass

