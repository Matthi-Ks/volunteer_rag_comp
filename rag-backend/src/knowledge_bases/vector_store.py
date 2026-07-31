import os
import chromadb

from chromadb.types import Collection
from rank_bm25 import BM25Okapi

from models.enums import InformationTier
from models.query import Query
from models.retrieval_result import RetrievalResult
from util.config_loader import load_config
from models.activity import Activity
from util.embedding_function import get_embedding_function

config = load_config()

class VectorStore:
    def __init__(self):
        os.makedirs(config["paths"]["vectordb"], exist_ok=True)

        self.db_client = chromadb.PersistentClient(config["paths"]["vectordb"])

        # create collections
        # it is required that the collectons name match information tier names in activity class
        self.collection_names = list(InformationTier)

        self.collections = {}
        for name in self.collection_names:
            self.collections[name]: Collection = self.db_client.get_or_create_collection(
                name=name.value,
                embedding_function=get_embedding_function()
            )

    def index(self, data: list[Activity]):
        self.clear_db()

        documents = {name: [] for name in self.collection_names}
        metadata = {name: [] for name in self.collection_names}
        ids = {name: [] for name in self.collection_names}

        for activity in data:
            for name in self.collection_names:
                metadata[name].append(activity.metadata.to_chromadb_metadata())
                ids[name].append(activity.id)
                documents[name].append(activity.text_variations.get(name)) # assuming that the collectons name match text variation names

        for name in self.collection_names:
            if documents[name]:
                self.collections[name].add(
                    documents = documents[name],
                    metadatas = metadata[name],
                    ids = ids[name]
                )


    def clear_db(self):
        for name in self.collection_names:
            ids = self.collections[name].get()["ids"]
            if ids:
                self.collections[name].delete(ids = ids)


    def clear_collection(self, collection_name):
        self.db_client.delete_collection(collection_name)

    # use semantic search only (dense embeddings)
    def semantic_similarity_search(self, query: Query, n: int = 10) -> list[RetrievalResult]:
        results = self.collections[query.options.informationTier].query(
            query_texts=list(query.text_variants.values()),
            n_results=n
        )

        return RetrievalResult.from_chroma_results(results, list(query.text_variants.keys()))

    # use BM25 algorithm for keyword search
    def bm25_search(self, query: Query, n: int = 10) -> list[RetrievalResult]:
        all_docs = self.collections[query.options.informationTier].get(
            include=["documents"],
        )

        tokenized_docs = [doc.lower().split() for doc in all_docs["documents"]]
        bm25 = BM25Okapi(tokenized_docs)

        bm25_results = []
        for query_text in list(query.text_variants.values()):
            tokenized_query = query_text.split()
            scores = bm25.get_scores(tokenized_query)
            top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:n]

            variation_res = []
            for idx in top_indices:
                doc_id = all_docs['ids'][idx]
                doc_text = all_docs['documents'][idx]
                score = scores[idx]
                variation_res.append((doc_id, doc_text, score))

            bm25_results.append(variation_res)

        return RetrievalResult.from_bm25_results(bm25_results, list(query.text_variants.keys()))



