import os
import instructor

from mistralai import Mistral
from openai import OpenAI, AsyncOpenAI
from ragas.llms import llm_factory
from ragas.embeddings.base import embedding_factory

from util.config_loader import load_config
from ollama import Client as OllamaClient

config = load_config()


class LLMFactory:
    @staticmethod
    def get_local_client() -> OllamaClient:
        return OllamaClient(
            host=config["ollama"]["host"]
        )

    @staticmethod
    def get_api_client() -> Mistral:
        api_key = os.getenv(config["mistral"]["api_key_env"])
        return Mistral(api_key=api_key)

    @classmethod
    def get_instructor_wrapping(cls):
        if config["use_local_llm"]:
            return instructor.from_provider(
                "ollama/" + config["ollama"]["model"],
                base_url=config["ollama"]["url"],
                mode=instructor.Mode.JSON,
            )
        else:
            api_key = os.getenv(config["mistral"]["api_key_env"])
            openai_client = OpenAI(
                api_key=api_key,
                base_url="https://api.mistral.ai/v1"
            )
            return instructor.from_openai(openai_client, mode=instructor.Mode.JSON)

    @classmethod
    def get_ragas_embedding_fn(cls):
        api_key = os.getenv(config["mistral"]["api_key_env"])
        async_mistral_client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.mistral.ai/v1"
        )
        return embedding_factory(
            model=config["mistral"]["embed"],
            provider="openai",
            client=async_mistral_client
        )

    @classmethod
    def get_ragas_llm(cls):

        if config["use_local_llm"]:
            async_client = AsyncOpenAI(
                api_key="ollama",
                base_url=f"{config['ollama']['url']}/v1"
            )
            llm = llm_factory(config["ollama"]["model"], provider="openai", client=async_client)
        else:
            api_key = os.getenv(config["mistral"]["api_key_env"])
            async_client = AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.mistral.ai/v1"
            )
            llm = llm_factory(config["mistral"]["model"], provider="openai", client=async_client)

        llm.is_async = True
        return llm