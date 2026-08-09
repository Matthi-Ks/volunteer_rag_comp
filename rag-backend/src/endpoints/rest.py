from fastapi import APIRouter, HTTPException

from knowledge_bases.evaluation_store import EvaluationStore
from knowledge_bases.graph_store import GraphStore
from knowledge_bases.vector_store import VectorStore
from models.query import Query
from models.enums import RagPipeline
from pipelines.fusion_rag.fusion_rag import FusionRag
from pipelines.graph_rag.graph_rag import GraphRag
from pipelines.hybrid_rag.hybrid_rag import HybridRag
from evaluation.eval import evaluate

router = APIRouter()
vector_store = VectorStore()
graph_store = GraphStore()
eval_store = EvaluationStore()

hybrid_rag = HybridRag(
    vectorStore=vector_store,
    graphStore=graph_store
)

fusion_rag = FusionRag(
    vectorStore=vector_store,
    graphStore=graph_store
)

graph_rag = GraphRag(
    vectorStore=vector_store,
    graphStore=graph_store
)

# gets a query object containing question versions as well as query options
@router.post("/search")
async def search(query: Query):
    try:
        if query.options.pipeline == RagPipeline.HYBRID:
            eval_results = await evaluate(query, hybrid_rag)
        elif query.options.pipeline == RagPipeline.FUSION:
            eval_results = await evaluate(query, fusion_rag)
        elif query.options.pipeline == RagPipeline.GRAPH:
            eval_results = await evaluate(query, graph_rag)
        else:
            raise Exception("Unknown rag pipeline")

        [eval_store.save_evaluation_result(result, query.options) for result in eval_results]

        return eval_results
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summaries")
async def get_pipeline_summaries():
    return eval_store.get_pipeline_averages()