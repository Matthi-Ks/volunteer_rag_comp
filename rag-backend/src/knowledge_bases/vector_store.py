import os
import chromadb

from chromadb.types import Collection
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
from models.query import Query
from util.config_loader import load_config
from models.activity import Activity
from util.embedding_function import get_embedding_function

#load mistral API key
load_dotenv()
config = load_config()

class VectorStore:
    def __init__(self):
        os.makedirs(config["paths"]["vectordb"], exist_ok=True)

        self.db_client = chromadb.PersistentClient(config["paths"]["vectordb"])

        # create collections
        # it is required that the collectons name match text variation names in activity class
        self.collection_names = [
            "title_only", # activity title only
            "title_softskill", # activity title only with associated softskills
            "title_desc", # all activty cols
            "title_desc_softskill" # all activity cols with associated softskills
        ]

        self.collections = {}
        for name in self.collection_names:
            self.collections[name]: Collection = self.db_client.get_or_create_collection(
                name=name,
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
                documents[name].append(getattr(activity.text_variations, name)) # assuming that the collectons name match text variation names

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
    def semantic_similarity_search(self, query: Query, n: int):
        filter = query.filter_values if query.options.useMetadataFilter else None
        results = self.collections[query.options.informationTier].query(
            query_text=query.query_text,
            where=filter,
            n=n
        )

        formatted = []
        if results['ids']:
            for idx in range(len(results['ids'][0])):
                formatted.append({
                    "id": results['ids'][0][idx],
                    "text": results['documents'][0][idx],
                    "metadata": results['metadatas'][0][idx]
                })
        return formatted

    # use BM25 algorithm for keyword search
    def bm25_search(self, query: Query, n: int):
        filter = query.filter_values if query.options.useMetadataFilter else None
        all_docs = self.collections[query.options.informationTier].get(
            include=["documents", "metadatas"],
            where=filter
        )

        tokenized_query = query.query_text.lower().split()
        tokenized_docs = [doc.lower().strip() for doc in all_docs["documents"]]
        bm25 = BM25Okapi(tokenized_docs)

        scores = bm25.get_scores(tokenized_query)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:n]

        formatted = []
        for idx in top_indices:
            formatted.append({
                "id": all_docs['ids'][idx],
                "text": all_docs['documents'][idx],
                "metadata": all_docs['metadatas'][idx] if all_docs['metadatas'] else {}
            })
        return formatted



