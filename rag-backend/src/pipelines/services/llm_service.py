import logging

from models.enums import QuestionVariant
from models.query import FusionRAGResponse
from util.config_loader import load_config
from util.llm_factory import LLMFactory

config = load_config()
logger = logging.getLogger(__name__)

REFORMULATE_SYSTEM_PROMPT = (
        "You are a precise RAG automation assistant. "
        "Generate alternative query variations for Fusion RAG searching."
    )

GEN_SYSTEM_PROMPT = (
        "You are a concise assistant. Answer the user's question using ONLY the provided context.\n\n"
        "CRITICAL RULES:\n"
        "1. Be brief; provide only a short description.\n"
        "2. Limit your answer to a maximum of 2-3 sentences or bullet points.\n"
        "3. Do not assume, extrapolate, or bring in outside knowledge.\n"
        "4. If the context does not contain the answer, say 'Information not found.' and nothing else.\n"
        "5. Use no special characters or special formatting."
    )

class LLMService:

    @classmethod
    def generate_answer(cls, query_text: str, context: list[str]) -> (str, int):
        messages =  cls._build_messages(query_text, context)

        if config["use_local_llm"]:
            client = LLMFactory.get_local_client()
            response = client.chat(
                model=config["ollama"]["model"],
                messages=messages
            )
            return response.get("message", {}).get("content",""), (response.get('prompt_eval_count', 0) + response.get('eval_count', 0))
        else:
            client = LLMFactory.get_api_client()
            response = client.chat.complete(
                model=config["mistral"]["model"],
                messages=messages
            )
            return response.choices[0].message.content, response.usage.total_tokens

    @classmethod
    def _build_messages(cls, query_text, context) -> list[dict[str,str]]:
        formatted_context = "\n---\n".join(context) if context else "No context provided."
        user_content = f"Context:\n{formatted_context}\n\nQuestion: {query_text}"

        return [
            {"role": "system", "content": GEN_SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ]

    @classmethod
    def reformulate_query_texts(cls, text_variants: dict[QuestionVariant, str]) -> (FusionRAGResponse, int):
        client = LLMFactory.get_instructor_wrapping()
        model_name = config["ollama"]["model"] if config["use_local_llm"] else config["mistral"]["model"]

        formatted_input = {
            (k.name.lower() if hasattr(k, "name") else str(k).lower()): v
            for k, v in text_variants.items()
        }

        user_prompt = f"""
                Given the following query variants, generate alternative phrasings for a Multi-Query / Fusion RAG system.

                Input Queries:
                {formatted_input}

                Instructions:
                1. Produce exactly 3 packets in the output list.
                2. Packet #1 MUST contain the exact original input queries.
                3. Packets #2 and #3 MUST contain new alternative phrasings using different synonyms.
                4. Maintain the exact same keys ('normal', 'abstract', 'detailed') across all packets.
                """

        try:
            structured_response, raw_output = client.chat.completions.create_with_completion(
                model=model_name,
                response_model=FusionRAGResponse,
                messages=[
                    {"role": "system", "content": REFORMULATE_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                max_retries=2
            )

            total_tokens = 0
            if raw_output.usage:
                total_tokens = raw_output.usage.total_tokens

            return structured_response, total_tokens

        except Exception as e:
            logger.error(f"Failed to generate query reformulations via Instructor: {e}")
            return [{k.name.lower() if hasattr(k, "name") else str(k).lower(): v for k, v in text_variants.items()}], 0



