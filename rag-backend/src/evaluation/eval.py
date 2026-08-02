import os
import sys
import types

from util.llm_factory import LLMFactory
from dotenv import load_dotenv
from ragas import experiment
from ragas.metrics.collections import Faithfulness, AnswerRelevancy, ContextRecall, ContextPrecision

from models.evaluation_result import EvaluationResult
from models.query import Query
from pipelines.rag_base import RagBase
from util.config_loader import load_config

config = load_config()
load_dotenv()

@experiment()
async def evaluate(query: Query, pipeline: RagBase) -> list[EvaluationResult]:
    llm_in_use = LLMFactory.get_ragas_llm()
    embeddings = LLMFactory.get_ragas_embedding_fn()

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
            token_count=answer.tokens_used,
            context=contexts,
            matching_skills=[] #todo
        ))

    return eval_results


