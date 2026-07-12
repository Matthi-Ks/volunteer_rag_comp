from models.pipeline_result import PipelineResult
from models.query import Query, FusionRAGResponse
from models.retrieval_result import RetrievalResult
from pipelines.rag_base import RagBase
from pipelines.services import FusionService, QueryPreprocessingService


class FusionRag(RagBase):

    #todo query reformulation and retrieval
    def execute_pipeline(self, query: Query) -> list[PipelineResult]:
        query_cpy = query.__deepcopy__()
        # todo include in token count
        reformulated_query_texts: FusionRAGResponse = self.llmService.reformulate_query_texts(query.text_variants)

        retrieval_result_set = []
        for variants in reformulated_query_texts:
            query_cpy.text_variants = variants
            vector_results: list[RetrievalResult] = self.vectorStore.semantic_similarity_search(query_cpy, n=5)
            retrieval_result_set.append(vector_results)

        merged_results: list[RetrievalResult] = FusionService.rrf(retrieval_result_set)

        text_contexts: list[list[str]] = self.rerankService.colbert_rerank(list(query.text_variants.values()),
                                                                           merged_results)

        responses: list[PipelineResult] = []
        for context, (questionVariant, query_text) in zip(text_contexts, query.text_variants.items()):
            resp = self.llmService.generate_answer(query_text, context)
            total_tokens = resp.get('prompt_eval_count', 0) + resp.get('eval_count', 0)
            responses.append(PipelineResult(
                used_context=context,
                model_response=resp.response,
                questionVariant=questionVariant,
                tokens_used=total_tokens
            ))

        return responses