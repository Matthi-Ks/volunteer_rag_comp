import sys
import types

from openai import AsyncOpenAI

from util.config_loader import load_config

fake_vertex_module = types.ModuleType("langchain_community.chat_models.vertexai")

class ChatVertexAI:
    pass

fake_vertex_module.ChatVertexAI = ChatVertexAI
sys.modules["langchain_community.chat_models.vertexai"] = fake_vertex_module

from mistralai import Mistral
from ragas import experiment
from ragas.metrics.collections import Faithfulness, AnswerRelevancy
from ragas.llms import llm_factory

from models.evaluation_result import EvaluationResult
from models.query import Query
from pipelines.rag_base import RagBase

config = load_config()

client = AsyncOpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)

llm = llm_factory(config["ollama"]["model"], provider="openai", client=client)
llm.is_async = True

@experiment()
async def evaluate(query: Query, pipeline: RagBase) -> list[EvaluationResult]:

    answers = pipeline.execute_pipeline(query)

    faithfulness_scorer = Faithfulness(llm=llm)
    #answer_relevancy_scorer = AnswerRelevancy(llm=llm)

    eval_results: list[EvaluationResult] = []
    for answer in answers:
        user_input_text = query.text_variants.get(answer.questionVariant)
        contexts = answer.used_context if answer.used_context is not None else []

        faithfulness = await faithfulness_scorer.ascore(
            response=answer.model_response,
            user_input=user_input_text,
            retrieved_contexts=contexts
        )

        eval_results.append(EvaluationResult(
            answer=answer.model_response,
            question_variant=answer.questionVariant,
            faithfulness=faithfulness.value,
            answer_relevance=0.0,
        ))

    return eval_results


