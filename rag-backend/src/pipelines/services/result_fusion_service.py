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

    @staticmethod
    def rrf_with_skill_boost(result_sets: list[list[RetrievalResult]], user_skills: list[str], k: int = 60) -> list[RetrievalResult]:
        merged_results = ResultFusionService.rrf(result_sets, k=k)

        if not user_skills:
            return merged_results

        user_skill_set = set(s.lower().strip() for s in user_skills)

        boost_alpha = None
        if boost_alpha is None:
            # 50% of the maximum single rank-1 RRF score (1.0 / (60 + 1))
            boost_alpha = 0.5 * (1.0 / (k + 1))

        for result in merged_results:
            doc_skills = result.associated_skills
            if not doc_skills:
                continue

            doc_skill_set = set(s.lower().strip() for s in doc_skills)
            if not doc_skill_set:
                continue

            intersection_count = len(user_skill_set.intersection(doc_skill_set))
            coverage_ratio = intersection_count / len(doc_skill_set)

            result.scores.rrf += boost_alpha * coverage_ratio

        return sorted(merged_results, key=lambda x: x.scores.rrf, reverse=True)
