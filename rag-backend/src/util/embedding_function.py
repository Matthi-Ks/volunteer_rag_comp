import os

from chromadb.utils.embedding_functions import MistralEmbeddingFunction

def get_embedding_function():
    return MistralEmbeddingFunction(
                    model= "mistral-embed",
                    api_key_env_var=os.getenv("MISTRAL_API_KEY")
                )