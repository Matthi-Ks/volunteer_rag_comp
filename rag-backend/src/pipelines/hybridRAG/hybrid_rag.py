from models.query import Query
from pipelines.rag_base import RagBase

class HybridRag(RagBase):
    def __init__(self, client, vectorStore):
        # llm client
        self.client = client
        self.vectorStore = vectorStore
        # todo move somewhere else
        self.reranker = RetrievalModel.from_pretrained('colbert-ir/colbertv2.0')

    def execute_pipeline(self, query: Query):
        query.text = self.__query_preprocessing(query.text)

        # retrieval
        retrieved_docs = self.hybrid_retrieval(query)

        # ranking
        ranked_docs = self.rank_retrieved_documents(retrieved_docs, query.text)

        return self.generate_answer()

    def hybrid_retrieval(self, query: Query):
        vector_results = self.vectorStore.semantic_similarity_search(query)
        bm25_results = self.vectorStore.bm25_search(query)

        return self.reciprocal_rank_fusion(vector_results, bm25_results)

    def rank_retrieved_documents(self, retrieved_docs):

        pass

    def generate_answer(self, retrieved_docs, query_text):
        self.colbert_ranking(retrieved_docs, query_text)
        pass

    def colbert_ranking(self, retrieved_docs, query_text):
        scores = self.reranker.score(queries=[query_text], documents=retrieved_docs)

    # todo implement more general version for all pipelines
    def reciprocal_rank_fusion(dense_results, bm25_results, k=60):
        rrf_scores = {}
        doc_registry = {d["id"]: d for d in (dense_results + bm25_results)}

        for rank, doc in enumerate(dense_results):
            rrf_scores[doc["id"]] = rrf_scores.get(doc["id"], 0.0) + (1.0 / (k + (rank + 1)))

        for rank, doc in enumerate(bm25_results):
            rrf_scores[doc["id"]] = rrf_scores.get(doc["id"], 0.0) + (1.0 / (k + (rank + 1)))

        sorted_ids = sorted(rrf_scores, key=rrf_scores.get, reverse=True)

        fused_results = []
        for doc_id in sorted_ids:
            doc_data = doc_registry[doc_id].copy()
            doc_data["rrf_score"] = rrf_scores[doc_id]
            fused_results.append(doc_data)

        return fused_results
