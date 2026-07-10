from models.query import Query
from models.retrieval_result import RetrievalResult
from pipelines.rag_base import RagBase
from pipelines.services import FusionService, QueryPreprocessingService


class HybridRag(RagBase):

    def execute_pipeline(self, query: Query):
        query.text_variations = QueryPreprocessingService.query_preprocessing(query.text_variations)

        vector_results: list[RetrievalResult] = self.vectorStore.semantic_similarity_search(query)
        bm25_results: list[RetrievalResult] = self.vectorStore.bm25_search(query)

        merged_results: list[RetrievalResult] = FusionService.rrf([vector_results, bm25_results])

        text_contexts: list[list[str]]  = self.rerankService.colbert_rerank(list(query.text_variations.values()), merged_results)

        responses = []
        for context, query_text in zip(text_contexts, list(query.text_variations.values())):
            resp = self.llmService.generate_answer(query_text, context)
            responses.append(resp)

        return responses