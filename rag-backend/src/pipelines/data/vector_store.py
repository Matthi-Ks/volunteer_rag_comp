import os
import chromadb

from chromadb import Knn, Rrf
from chromadb.types import Collection
from chromadb.utils.embedding_functions import MistralEmbeddingFunction, ChromaBm25EmbeddingFunction
from dotenv import load_dotenv
from pipelines.data.util.config_loader import load_config
from pipelines.data.models.activity import Activity

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
                embedding_function=MistralEmbeddingFunction(
                    model= "mistral-embed",
                    api_key_env_var="MISTRAL_API_KEY"
                ),
                sparse_embedding_function=ChromaBm25EmbeddingFunction()
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
    def semantic_similarity_search(self, collection: str, query_text: str, n: int):
        return self.collections[collection].query(
            query_text=query_text,
            n=n
        )

    # use semantic search + BM25 (dense + sparse embeddings)
    def hybrid_search(self, collection: str, query_text: str):
        return self.collections[collection].search(
            search = [
                Knn(query_texts=query_text, n_results=10),
                Rrf(query_texts=query_text, k=60)
            ],
            n_results=5
        )


