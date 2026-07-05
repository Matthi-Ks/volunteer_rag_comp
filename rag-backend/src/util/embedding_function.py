from chromadb.utils.embedding_functions import MistralEmbeddingFunction
from dotenv import load_dotenv

load_dotenv()

def get_embedding_function():
    return MistralEmbeddingFunction(
                    model= "mistral-embed",
                    api_key_env_var="MISTRAL_API_KEY"
                )