from pipelines.data.config_loader import load_config
from pipelines.data.data_utility import DataUtility
from pipelines.data.vector_store import VectorStore

config = load_config()

def main():
    vector_store = VectorStore()
    if config["mode"] == "indexing":
        data_util = DataUtility()
        if not config["keep_data"]:
            processed_data = data_util.process_data()
        else:
            processed_data = data_util.load_processed_data()

        if not config["keep_vectordb"]:
            vector_store.index(processed_data)


    elif config["mode"] == "rag":
        print("not implemented yet")

    else:
        raise RuntimeError("Choose either \"indexing\" or \"rag\" as application mode in config.yml")

if __name__ == "__main__":
    main()