import uvicorn
from fastapi import Request, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from knowledge_bases.knowledge_graph_store import KnowledgeGraphStore
from knowledge_bases.vector_store import VectorStore
from util.config_loader import load_config
from util.pre_processing_utility import PreProcessingUtility
from endpoints.rest import router

config = load_config()

def run_indexing():
    vector_store = VectorStore()
    kg_store = KnowledgeGraphStore()
    data_util = PreProcessingUtility()
    if not config["keep_data"]:
        processed_data = data_util.process_data()
    else:
        processed_data = data_util.load_processed_data()

    if not config["keep_vectordb"]:
        vector_store.index(processed_data)

    if not config["keep_knowledge_graph"]:
        kg_store.build_graphs(processed_data)
        # plot graph
        # knowledgeGraph.plot_graph(knowledgeGraph.title_graph)
    else:
        kg_store.load_graphs()

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

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("--- DETAILED VALIDATION ERROR ---")
    print(exc.errors())
    print("---------------------------------")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

def main():
    if config["mode"] == "indexing":
        run_indexing()
    elif config["mode"] == "rag":
        uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=False)
    else:
        raise RuntimeError("Choose either \"indexing\" or \"rag\" as application mode in config.yml")

if __name__ == "__main__":
    main()