from fastapi import APIRouter, HTTPException

from knowledge_bases.knowledge_graph_store import KnowledgeGraphStore
from knowledge_bases.vector_store import VectorStore
from models.evaluation_result import EvaluationResult
from models.query import Query
from models.enums import RagPipeline, QuestionVariant
from pipelines.fusion_rag.fusion_rag import FusionRag
from pipelines.hybrid_rag.hybrid_rag import HybridRag
from pipelines.services import RerankingService, LLMService
from evaluation.eval import evaluate

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

fusion_rag = FusionRag(
    vectorStore=vector_store,
    kg_store=kg_store,
    rerankService=rerank_service,
    llmService=llm_service
)

# gets a query object containing question versions as well as query options
@router.post("/search")
async def search(query: Query):
    try:
        eval_result: list[EvaluationResult] = []
        if query.options.pipeline == RagPipeline.HYBRID:
            eval_result = await evaluate(query, hybrid_rag)
        elif query.options.pipeline == RagPipeline.FUSION:
            eval_result = await evaluate(query, fusion_rag)
        elif query.options.pipeline == RagPipeline.GRAPH:
            print("graph")
        else:
            print("unknown pipeline")

        return {
            "status": "success",
            "results": eval_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test")
async def test(query: Query):
    try:
        print(query)
        return [EvaluationResult(
                token_count=100,
                context_recall=1.0,
                context_precision=0.7,
                faithfulness=0.7,
                answer_relevance=0.6,
                answer="Test answer",
                question_variant=QuestionVariant.NORMAL
            )]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))