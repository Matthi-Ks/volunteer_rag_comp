from knowledge_bases.knowledge_graph_store import KnowledgeGraphStore
from knowledge_bases.vector_store import VectorStore
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
    print("not implemented yet")

def main():
    if config["mode"] == "indexing":
        run_indexing()
    elif config["mode"] == "rag":
        run_rag()

    else:
        raise RuntimeError("Choose either \"indexing\" or \"rag\" as application mode in config.yml")

if __name__ == "__main__":
    main()