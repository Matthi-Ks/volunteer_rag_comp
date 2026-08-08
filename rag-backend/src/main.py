import sys
import types

fake_vertex_module = types.ModuleType("langchain_community.chat_models.vertexai")

class ChatVertexAI:
    pass

fake_vertex_module.ChatVertexAI = ChatVertexAI
sys.modules["langchain_community.chat_models.vertexai"] = fake_vertex_module

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from knowledge_bases.vector_store import VectorStore
from knowledge_bases.graph_store import GraphStore
from util.config_loader import load_config
from util.pre_processing_utility import PreProcessingUtility
from endpoints.rest import router

config = load_config()

def run_indexing():
    vector_store = VectorStore()
    graph_store = GraphStore()

    data_util = PreProcessingUtility()
    if not config["keep_data"]:
        processed_data = data_util.process_data()
    else:
        processed_data = data_util.load_processed_data()

    if not config["keep_vectordb"]:
        vector_store.index(processed_data)

    if not config["keep_knowledge_graph"]:
        graph_store.setup_db_indexes()
        graph_store.indexing(processed_data)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Volunteer RAG API",
        version="1.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api", tags=["RAG Endpoints"])
    return app

app = create_app()

def main():
    if config["mode"] == "indexing":
        run_indexing()
    elif config["mode"] == "rag":
        uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=False)
    else:
        raise RuntimeError("Choose either \"indexing\" or \"rag\" as application mode in config.yml")

if __name__ == "__main__":
    main()