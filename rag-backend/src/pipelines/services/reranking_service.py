import logging

from pylate import rank, models

from models.enums import QuestionVariant
from models.retrieval_result import RetrievalResult
from util.config_loader import load_config

config = load_config()
logger = logging.getLogger(__name__)

class RerankingService:

    _colbert_model: models.ColBERT | None = None

    @classmethod
    def get_colbert_model(cls) -> models.ColBERT:
        if cls._colbert_model is None:
            logger.info("Loading ColBERT reranking model into memory")
            cls._colbert_model = models.ColBERT(
                model_name_or_path="lightonai/GTE-ModernColBERT-v1",
                cache_folder=config["paths"]["HFcache"]
            )
        return cls._colbert_model

    @classmethod
    def colbert_rerank(cls, query_texts: list[str], retrieved_res: list[RetrievalResult], n_final: int = 5) -> list[list[str]]:
        model = cls.get_colbert_model()

        queries_embeddings = model.encode(query_texts, is_query=True)

        variant_index_map = {
            QuestionVariant.NORMAL: 0,
            QuestionVariant.ABSTRACT: 1,
            QuestionVariant.DETAILED: 2,
        }
        doc_texts: list[list[str]] = [[], [], []]

        for doc in retrieved_res:
            idx = variant_index_map.get(doc.origin_variation, 0)
            doc_texts[idx].append(doc.text)

        doc_embeddings = []
        for set in doc_texts:
            if set:
                embeddings = model.encode(set, is_query=False)
                doc_embeddings.append(embeddings)
            else:
                logger.warning("Empty document set encountered during reranking variant processing.")

        unique_docs = {doc.id: doc for doc in retrieved_res}

        all_ids = list(unique_docs.keys())
        nested_ids = [all_ids for _ in query_texts]

        reranked_batches = rank.rerank(
            documents_ids=nested_ids,
            queries_embeddings=queries_embeddings,
            documents_embeddings=doc_embeddings
        )

        final_context = []
        for colbert_batch in reranked_batches:
            sorted_batch = [
                unique_docs[res["id"]].text
                for res in colbert_batch[:n_final]
                if res["id"] in unique_docs
            ]
            final_context.append(sorted_batch)

        return final_context