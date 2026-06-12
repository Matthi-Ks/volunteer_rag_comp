from pipelines.data.csv_data_utility import CSVDataUtility
from pipelines.data.vector_store import VectorStore

FILE_PATH = "../../resources/final_sample.csv"

def main():
    csv_util = CSVDataUtility(FILE_PATH)
    processed_data = csv_util.textify_csv()
    csv_util.save_as_json(processed_data)

    #vector_store = VectorStore()
    #vector_store.index(data)

if __name__ == "__main__":
    main()