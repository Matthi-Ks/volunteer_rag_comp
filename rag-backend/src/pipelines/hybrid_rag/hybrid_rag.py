from models.pipeline_result import PipelineResult
from models.query import Query
from models.retrieval_result import RetrievalResult
from pipelines.rag_base import RagBase
from pipelines.services import FusionService, QueryPreprocessingService


class HybridRag(RagBase):

    def execute_pipeline(self, query: Query) -> list[PipelineResult]:
        query.text_variants = QueryPreprocessingService.query_preprocessing(query.text_variants)

        vector_results: list[RetrievalResult] = self.vectorStore.semantic_similarity_search(query)
        bm25_results: list[RetrievalResult] = self.vectorStore.bm25_search(query)

        merged_results: list[RetrievalResult] = FusionService.rrf([vector_results, bm25_results])

        text_contexts: list[list[str]]  = self.rerankService.colbert_rerank(list(query.text_variants.values()), merged_results)

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