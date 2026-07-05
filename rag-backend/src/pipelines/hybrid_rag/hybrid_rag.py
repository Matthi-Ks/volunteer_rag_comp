from models.query import Query
from pipelines.rag_base import RagBase
from pipelines.services import FusionService


class HybridRag(RagBase):

    def execute_pipeline(self, query: Query):
        query.text = self.__query_preprocessing(query.text)

        vector_results = self.vectorStore.semantic_similarity_search(query)
        bm25_results = self.vectorStore.bm25_search(query)

        merged_results = FusionService.rrf([vector_results, bm25_results])

        reranked_results = self.rerankService.colbert_rerank(query.text, merged_results, 20)

        self.llmService.generate_answer(query.text, reranked_results)
