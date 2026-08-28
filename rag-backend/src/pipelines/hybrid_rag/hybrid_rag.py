from models.pipeline_result import PipelineResult
from models.query import Query
from models.retrieval_result import RetrievalResult
from pipelines.rag_base import RagBase
from pipelines.services.llm_service import LLMService
from pipelines.services.query_preprocessing_service import QueryPreprocessingService
from pipelines.services.reranking_service import RerankingService
from pipelines.services.result_fusion_service import ResultFusionService

class HybridRag(RagBase):

    def execute_pipeline(self, query: Query) -> list[PipelineResult]:
        query = QueryPreprocessingService.query_preprocessing(query)

        vector_results: list[RetrievalResult] = self.vectorStore.semantic_similarity_search(query, 10)
        bm25_results: list[RetrievalResult] = self.vectorStore.bm25_search(query, 10)

        if query.options.useESCOSkills:
            merged_results: list[RetrievalResult] = ResultFusionService.rrf_with_skill_boost([vector_results, bm25_results], query.profile.esco_skills, query.options.useESCOSkills)
        else:
            merged_results: list[RetrievalResult] = ResultFusionService.rrf([vector_results, bm25_results])

        text_contexts: list[list[str]]  = RerankingService.colbert_rerank(list(query.text_variants.values()), merged_results, 5)

        responses: list[PipelineResult] = []
        for context, (questionVariant, query_text) in zip(text_contexts, query.text_variants.items()):
            resp: (str, int) = LLMService.generate_answer(query_text, context)
            responses.append(PipelineResult(
                used_context=context,
                model_response=resp[0],
                questionVariant=questionVariant,
                tokens_used=resp[1]
            ))

        return responses