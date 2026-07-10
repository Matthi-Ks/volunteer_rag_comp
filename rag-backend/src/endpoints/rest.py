from fastapi import APIRouter, HTTPException

from knowledge_bases.knowledge_graph_store import KnowledgeGraphStore
from knowledge_bases.vector_store import VectorStore
from models.query import Query, RAGPipeline
from pipelines.hybrid_rag.hybrid_rag import HybridRag
from pipelines.services import RerankingService, LLMService

router = APIRouter()
vector_store = VectorStore()
kg_store = KnowledgeGraphStore()
rerank_service = RerankingService()
llm_service = LLMService()

hybrid_rag = HybridRag(
        vectorStore=vector_store,
        kg_store=kg_store,
        rerankService=rerank_service,
        llmService=llm_service
    )

@router.post("/search")
async def search(query: Query):
    try:
        responses = []
        if query.options.pipeline == RAGPipeline.HYBRID:
            responses = hybrid_rag.execute_pipeline(query)

        return {
            "status": "success",
            "results": responses
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hello")
async def hello():
    return {
        "status": "success",
        "msg": "Hello"
    }