
class FusionService:
    # reciprocal rank fusion
    @staticmethod
    def rrf(self, result_sets: list, k: int = 60):
        pass

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