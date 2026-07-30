from models.retrieval_result import RetrievalResult

class ResultFusionService:

    # reciprocal rank fusion
    @staticmethod
    def rrf(result_sets: list[list[RetrievalResult]], k: int = 60) -> list[RetrievalResult]:
        rrf_scores: dict[str, float] = {}
        for result_set in result_sets:
            for rank, result in enumerate(result_set, start=1):
                if result.id not in rrf_scores:
                    rrf_scores[result.id] = 0.0
                rrf_scores[result.id] += 1.0 / (k + rank)

        merged_dict = {}
        for result_set in result_sets:
            for result in result_set:
                key = (result.id, result.origin_variation)

                if key not in merged_dict:
                    cloned_result = result.model_copy(deep=True)
                    cloned_result.scores.rrf = rrf_scores[result.id]
                    merged_dict[key] = cloned_result

        return sorted(merged_dict.values(), key=lambda x: x.scores.rrf, reverse=True)