from abc import ABC, abstractmethod

from models.pipeline_result import PipelineResult
from models.query import Query


class RagBase(ABC):
    def __init__(self, vectorStore, graphStore):
        self.vectorStore = vectorStore
        self.graphStore = graphStore

    # takes a query object and generates an answer for each question variant
    @abstractmethod
    def execute_pipeline(self, query: Query) -> list[PipelineResult]:
        pass

