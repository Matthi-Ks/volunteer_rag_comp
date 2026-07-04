from pipelines.data.knowledge_graph import KnowledgeGraph
from pipelines.data.util.config_loader import load_config
from pipelines.data.util.data_utility import DataUtility
from pipelines.data.vector_store import VectorStore

config = load_config()

def main():
    vector_store = VectorStore()
    knowledgeGraph = KnowledgeGraph()
    if config["mode"] == "indexing":
        data_util = DataUtility()
        if not config["keep_data"]:
            processed_data = data_util.process_data()
        else:
            processed_data = data_util.load_processed_data()

        if not config["keep_vectordb"]:
            vector_store.index(processed_data)

        if not config["keep_knowledge_graph"]:
            knowledgeGraph.build_graphs(processed_data)
            # plot graph
            knowledgeGraph.plot_graph(knowledgeGraph.title_graph)

    elif config["mode"] == "rag":
        print("not implemented yet")

    else:
        raise RuntimeError("Choose either \"indexing\" or \"rag\" as application mode in config.yml")

if __name__ == "__main__":
    main()