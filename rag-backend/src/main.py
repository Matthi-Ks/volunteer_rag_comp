from knowledge_bases import KnowledgeGraphStore
from util.config_loader import load_config
from util.pre_processing_utility import PreProcessingUtility
from knowledge_bases import VectorStore

config = load_config()

def main():
    vector_store = VectorStore()
    knowledgeGraph = KnowledgeGraphStore()
    if config["mode"] == "indexing":
        data_util = PreProcessingUtility()
        if not config["keep_data"]:
            processed_data = data_util.process_data()
        else:
            processed_data = data_util.load_processed_data()

        if not config["keep_vectordb"]:
            vector_store.index(processed_data)

        if not config["keep_knowledge_graph"]:
            knowledgeGraph.build_graphs(processed_data)
            # plot graph
            #knowledgeGraph.plot_graph(knowledgeGraph.title_graph)
        else:
            knowledgeGraph.load_graphs()

    elif config["mode"] == "rag":
        print("not implemented yet")

    else:
        raise RuntimeError("Choose either \"indexing\" or \"rag\" as application mode in config.yml")

if __name__ == "__main__":
    main()