from matplotlib.patheffects import Normal

from knowledge_bases.knowledge_graph_store import KnowledgeGraphStore
from knowledge_bases.vector_store import VectorStore
from models.activity import ActivityMetadata
from models.query import Query, QueryOptions, InformationTier, RAGPipeline, QueryTextVariation
from pipelines.hybrid_rag.hybrid_rag import HybridRag
from pipelines.services import RerankingService, LLMService
from util.config_loader import load_config
from util.pre_processing_utility import PreProcessingUtility

config = load_config()

vector_store = VectorStore()
kg_store = KnowledgeGraphStore()

def run_indexing():
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

def run_rag():
    query = Query(
        text_variations={
            QueryTextVariation.NORMAL: "I want to volunteer preferably doing administrative tasks",
            QueryTextVariation.ABSTRACT: "I want to volunteer preferably doing administrative tasks",
            QueryTextVariation.DETAILED: "I want to volunteer preferably doing administrative tasks"
        },
        options=QueryOptions(
            useMetadataFilter=False,
            informationTier=InformationTier.TITLE_DESC_SOFTSKILL,
            pipeline=RAGPipeline.HYBRID
        ),
        filter_values=ActivityMetadata(
            location="",
            starting_date="",
            end_date=None
        )
    )
    hybrid_rag = HybridRag(
        vectorStore=vector_store,
        kg_store=kg_store,
        rerankService=RerankingService(),
        llmService=LLMService()
    )
    hybrid_rag.execute_pipeline(query)

def main():
    if config["mode"] == "indexing":
        run_indexing()
    elif config["mode"] == "rag":
        run_rag()
    else:
        raise RuntimeError("Choose either \"indexing\" or \"rag\" as application mode in config.yml")

if __name__ == "__main__":
    main()