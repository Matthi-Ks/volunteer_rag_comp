import os
import sys
import types

fake_vertex_module = types.ModuleType("langchain_community.chat_models.vertexai")

class ChatVertexAI:
    pass

fake_vertex_module.ChatVertexAI = ChatVertexAI
sys.modules["langchain_community.chat_models.vertexai"] = fake_vertex_module

from dotenv import load_dotenv
from openai import AsyncOpenAI
from ragas import experiment
from ragas.metrics.collections import Faithfulness, AnswerRelevancy, ContextRecall, ContextPrecision
from ragas.llms import llm_factory
from ragas.embeddings.base import embedding_factory

from models.evaluation_result import EvaluationResult
from models.query import Query
from pipelines.rag_base import RagBase
from util.config_loader import load_config

config = load_config()
load_dotenv()

client = AsyncOpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)

mistral_api_client = AsyncOpenAI(
    api_key=os.getenv("MISTRAL_API_KEY"),
    base_url="https://api.mistral.ai/v1"
)

local_llm = llm_factory(config["ollama"]["model"], provider="openai", client=client)
local_llm.is_async = True

api_llm = llm_factory("mistral-large-latest", provider="openai", client=mistral_api_client)
api_llm.is_async = True

embeddings = embedding_factory(model="mistral-embed", provider="openai", client=mistral_api_client)

@experiment()
async def evaluate(query: Query, pipeline: RagBase) -> list[EvaluationResult]:
    llm_in_use = local_llm if config["use_local_eval_llm"] else mistral_api_client
    answers = pipeline.execute_pipeline(query)

    faithfulness_scorer = Faithfulness(llm=llm_in_use)
    answer_relevancy_scorer = AnswerRelevancy(llm=llm_in_use, embeddings=embeddings)
    context_recall_scorer = ContextRecall(llm=llm_in_use)
    context_precision_scorer = ContextPrecision(llm=llm_in_use)

    eval_results: list[EvaluationResult] = []
    for answer in answers:
        user_input_text = query.text_variants.get(answer.questionVariant)
        contexts = answer.used_context if answer.used_context is not None else []

        faithfulness = await faithfulness_scorer.ascore(
            response=answer.model_response,
            user_input=user_input_text,
            retrieved_contexts=contexts
        )

        answer_relevancy = await answer_relevancy_scorer.ascore(
            response=answer.model_response,
            user_input=user_input_text
        )

        context_recall = await context_recall_scorer.ascore(
            user_input=user_input_text,
            retrieved_contexts=contexts,
            reference="Administrative Tasks"
        )

        context_precision = await context_precision_scorer.ascore(
            user_input=user_input_text,
            retrieved_contexts=contexts,
            reference="Administrative Tasks"
        )

        eval_results.append(EvaluationResult(
            answer=answer.model_response,
            question_variant=answer.questionVariant,
            faithfulness=faithfulness.value,
            answer_relevance=answer_relevancy.value,
            context_recall=context_recall.value,
            context_precision=context_precision.value,
            token_count=answer.tokens_used
        ))

    return eval_results


