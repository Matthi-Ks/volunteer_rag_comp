import os
import chromadb

DB_PATH = "src/resources/vector_store"

class VectorStore:
    def __init__(self):
        # create dir if non-existent
        os.makedirs(DB_PATH, exist_ok=True)
        # init chromaDB
        self.db_client = chromadb.PersistentClient(DB_PATH)
        self.embedding_fn = None # research mistral embeddings

        #create collections
        self.collection_names = [
            "title_only", # activity title only
            "title_softskill", # activity title only with associated softskills
            "title_desc", # all activty cols
            "title_desc_softskill" # all activity cols with associated softskills
        ]

        self.collections = {}
        for name in self.collection_names:
            self.collections[name] = self.db_client.get_or_create_collection(
                name=name,
                embedding_function=self.embedding_fn
            )


    # think about adding metadata as cols in csv
    def index(self, data):
        print("indexing data")




