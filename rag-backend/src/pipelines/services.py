import json

from pylate import models, rank
from ollama import Client

from models.enums import QuestionVariant, InformationTier
from models.query import FusionRAGResponse
from models.retrieval_result import RetrievalResult
from util.config_loader import load_config

config = load_config()

class QueryPreprocessingService:
    # strip input text of unwanted symbols and formating
    @staticmethod
    def query_preprocessing(variations: dict[QuestionVariant,str]) -> dict[QuestionVariant,str]:
        # todo maybe implement regex to only allow a-zA-Z0-9
        for key in variations.keys():
            variations[key] = " ".join(variations[key].lower().strip().split())
        return variations

class FusionService:
    # reciprocal rank fusion
    @staticmethod
    def rrf(result_sets: list[list[RetrievalResult]], k: int = 60) -> list[RetrievalResult]:
        rrf_scores: dict[str, float] = {}
        for result_set in result_sets:
            for rank, result in enumerate(result_set, start=1):
                if result.id not in rrf_scores:
                    rrf_scores[result.id] = 0.0
                rrf_scores[result.id] += 1.0 / (k + rank)

        merged_dict = {}
        for result_set in result_sets:
            for result in result_set:
                key = (result.id, result.origin_variation)

                if key not in merged_dict:
                    cloned_result = result.model_copy(deep=True)
                    cloned_result.scores.rrf = rrf_scores[result.id]
                    merged_dict[key] = cloned_result

        return sorted(merged_dict.values(), key=lambda x: x.scores.rrf, reverse=True)

class RerankingService:
    def __init__(self):
        self._colbert_model = None

    @property
    def colbert_model(self):
        if self._colbert_model is None:
            self._colbert_model = models.ColBERT(
                model_name_or_path="lightonai/GTE-ModernColBERT-v1",
                cache_folder=config["paths"]["HFcache"]
            )
        return self._colbert_model

    # handles more than one query if necessary
    def colbert_rerank(self, query_texts: list[str], retrieved_res: list[RetrievalResult], n_final: int = 10) -> list[list[str]]:
        queries_embeddings = self.colbert_model.encode(query_texts, is_query=True)

        doc_texts: list[list[str]] = [[],[],[]]
        for doc in retrieved_res:
            if doc.origin_variation == QuestionVariant.NORMAL:
                doc_texts[0].append(doc.text)
            elif doc.origin_variation == QuestionVariant.ABSTRACT:
                doc_texts[1].append(doc.text)
            else:
                doc_texts[2].append(doc.text)

        doc_embeddings = []
        for set in doc_texts:
            if set:
                embeddings = self.colbert_model.encode(set, is_query=False)
                doc_embeddings.append(embeddings)
            else:
                print("something is wrong")

        unique_docs = {}
        for elem in retrieved_res:
            if elem.id not in unique_docs:
                unique_docs[elem.id] = elem

        all_ids = [doc.id for doc in unique_docs.values()]
        nested_ids = [all_ids for _ in query_texts]

        reranked_batches = rank.rerank(
            documents_ids=nested_ids,
            queries_embeddings=queries_embeddings,
            documents_embeddings=doc_embeddings
        )

        doc_lookup = {doc.id: doc for doc in unique_docs.values()}
        final_context = []

        for colbert_batch in reranked_batches:
            sorted_batch = []
            for res in colbert_batch[:n_final]:
                doc_id = res["id"]
                sorted_batch.append(doc_lookup[doc_id].text)
            final_context.append(sorted_batch)

        return final_context


class LLMService:
    def __init__(self):
        self.client = Client(
            host=config["ollama"]["host"]
        )

    # todo experiment with llm restraints
    def generate_answer(self, query_text: str, context: list[str]):
        joined_context = "\n---\n".join(context)
        augmented_prompt = f"""
You are a concise assistant. Answer the user's question using ONLY the provided context.
---
CRITICAL RULES:
1. Be brief, only provide a short description 
2. Limit your answer to a maximum of 2-3 sentences (or bullet points).
3. Do not assume, extrapolate, or bring in outside knowledge.
4. If the context does not contain the answer, say "Information not found." and nothing else.
5. Use no special characters or any kind of special formating
---
Context:
{joined_context}
---
Question: {query_text}
Answer:"""

        response = self.client.generate(
            model=config["ollama"]["model"],
            prompt=augmented_prompt
        )

        return response

    def reformulate_query_texts(self, text_variants: dict[QuestionVariant, str]) -> list[dict[QuestionVariant, str]]:
        formatted_input = json.dumps({k.name if hasattr(k, 'name') else str(k): v for k, v in text_variants.items()},
                                     indent=2)

        prompt = (
            f"You are an AI assistant tasked with generating alternative formulations for a Multi-Query / Fusion RAG system.\n"
            f"You will receive a JSON object containing different question variants.\n"
            f"Your job is to generate 3 alternative variations for EACH variant provided, capturing different synonyms and phrasings.\n\n"
            f"Input Variants:\n{formatted_input}\n\n"
            f"Instructions:\n"
            f"1. Create a list containing 3 dictionaries in total.\n"
            f"2. The FIRST dictionary in the list MUST contain the exact original queries you received as input.\n"
            f"3. The following 2 dictionaries must contain the newly generated alternative phrasings.\n"
            f"4. Keep the exact same keys (QuestionVariant names) in every dictionary.\n\n"
            f"Output MUST strictly follow this JSON schema:\n"
            f"{{ 'packets': [ "
            f"  {{ 'normal': 'original...', 'abstract': 'original...', 'detailed': 'original...' }}, "
            f"  {{ 'normal': 'alt 1...', 'abstract': 'alt 1...', 'detailed': 'alt 1...' }}, "
            f"  {{ 'normal': 'alt 2...', 'abstract': 'alt 2...', 'detailed': 'alt 2...' }}, "
            f"  {{ 'normal': 'alt 3...', 'abstract': 'alt 3...', 'detailed': 'alt 3...' }} "
            f"] }}"
        )

        response = self.client.chat(
            model=config["ollama"]["model"],
            messages=[
                {"role": "system",
                 "content": "You are a precise RAG automation assistant that outputs ONLY valid JSON matching the schema without any conversational text."},
                {"role": "user", "content": prompt}
            ],
            format=FusionRAGResponse.model_json_schema()
        )

        try:
            response_content = response.get('message', {}).get('content', '{}')
            parsed_json = json.loads(response_content)
            packets = parsed_json.get("packets", [])

            cleaned_packets = [
                {k.lower(): v for k, v in packet.items()}
                for packet in packets
            ]

            if cleaned_packets:
                return cleaned_packets

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing bulk Fusion RAG response from Ollama: {e}")

        # fallback: original list
        return [text_variants]