from models.query import Query


class QueryPreprocessingService:

    # strip input text of unwanted symbols and formating
    @staticmethod
    def query_preprocessing(query: Query) -> Query:
        metadata_prefix = ""
        if query.options.useMetadataFilter and query.filter_values:
            metadata_prefix = f"Metadata: [Region: {query.filter_values.region}] [Timeframe: {query.filter_values.timeframe}] "

        for key in query.text_variants.keys():
            clean_text = " ".join(query.text_variants[key].lower().strip().split())
            query.text_variants[key] = f"{metadata_prefix}{clean_text}"

        return query