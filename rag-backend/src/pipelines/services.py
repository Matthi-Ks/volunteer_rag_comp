
class FusionService:
    # reciprocal rank fusion
    @staticmethod
    def rrf(self, result_sets: list, k: int = 60):
        merged_dict = {}

        for result_set in result_sets:
            for rank, result in enumerate(result_set, start=1):
                doc_id = result["id"]

                if doc_id not in merged_dict:
                    result["rrf_score"] = 0.0
                    merged_dict[doc_id] = result

                merged_dict[doc_id]["rrf_score"] += 1 / (k + rank)

        return sorted(merged_dict.values(), key=lambda x: x["rrf_score"], reverse=True)

class RerankingService:
    def __init__(self):
        self.model = "" # todo

    def colbert_rerank(self, query_text: str, retrieved_res: list, n_final: int):
        pass

class LLMService:
    def __init__(self):
        self.client = "" #todo

    def generate_answer(self, query_text: str, context: list):
        pass