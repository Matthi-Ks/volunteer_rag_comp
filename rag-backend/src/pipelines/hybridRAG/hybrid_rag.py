from pipelines.data.models.query import Query


class HybridRag:
    def __init__(self, client, vectorStore):
        # llm client
        self.client = client
        self.vectorStore = vectorStore
        pass

    def execute_pipeline(self, query: Query):
        self.__query_preprocessing(query.text)

        # retrieval
        retrieved_docs = self.hybrid_retrieval()

        # ranking
        ranked_docs = self.rank_retrieved_documents()

        return self.generate_answer()

    # handles query embedding and reformulation
    def __query_preprocessing(self, query: str) -> str:
        pass

    def hybrid_retrieval(self):
        pass

    def rank_retrieved_documents(self):
        pass

    def generate_answer(self):
        pass