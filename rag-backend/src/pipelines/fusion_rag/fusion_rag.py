from models.fusion_query_packet import FusionRAGResponse
from models.pipeline_result import PipelineResult
from models.query import Query
from models.retrieval_result import RetrievalResult
from pipelines.rag_base import RagBase
from pipelines.services.llm_service import LLMService
from pipelines.services.query_preprocessing_service import QueryPreprocessingService
from pipelines.services.reranking_service import RerankingService
from pipelines.services.result_fusion_service import ResultFusionService


class FusionRag(RagBase):

    def execute_pipeline(self, query: Query) -> list[PipelineResult]:
        ref_resp = LLMService.reformulate_query_texts(query.text_variants)
        reformulated_query_texts: FusionRAGResponse = ref_resp[0]
        ref_tokens = ref_resp[1]

        retrieval_result_set = []
        for variants in reformulated_query_texts.packets:
            query_cpy = query.__deepcopy__()
            query_cpy.text_variants = variants

            query_cpy = QueryPreprocessingService.query_preprocessing(query_cpy)
            vector_results: list[RetrievalResult] = self.vectorStore.semantic_similarity_search(query_cpy, n=10)
            retrieval_result_set.append(vector_results)

        if query.options.useESCOSkills:
            merged_results: list[RetrievalResult] = ResultFusionService.rrf_with_skill_boost(retrieval_result_set, query.profile.esco_skills)
        else:
            merged_results: list[RetrievalResult] = ResultFusionService.rrf(retrieval_result_set)

        text_contexts: list[list[str]] = RerankingService.colbert_rerank(list(query.text_variants.values()), merged_results, 5)

        responses: list[PipelineResult] = []
        for context, (questionVariant, query_text) in zip(text_contexts, query.text_variants.items()):
            resp = LLMService.generate_answer(query_text, context)
            responses.append(PipelineResult(
                used_context=context,
                model_response=resp[0],
                questionVariant=questionVariant,
                tokens_used=resp[1]+ref_tokens
            ))

        return responses