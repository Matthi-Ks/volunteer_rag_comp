import json

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

with open(config["paths"]["reference_answers"], "r", encoding="utf-8") as f:
    REFERENCE_DATA = json.load(f)

@experiment()
async def evaluate(query: Query, pipeline: RagBase) -> list[EvaluationResult]:
    llm_in_use = LLMFactory.get_ragas_llm()
    embeddings = LLMFactory.get_ragas_embedding_fn()

    answers = pipeline.execute_pipeline(query)

    faithfulness_scorer = Faithfulness(llm=llm_in_use)
    answer_relevancy_scorer = AnswerRelevancy(llm=llm_in_use, embeddings=embeddings)
    context_recall_scorer = ContextRecall(llm=llm_in_use)
    context_precision_scorer = ContextPrecision(llm=llm_in_use)

    reference_text = get_reference_answer(
        region=query.filter_values.region,
        timeframe=query.filter_values.timeframe,
        question_id=query.query_id
    )

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
            reference=reference_text
        )

        context_precision = await context_precision_scorer.ascore(
            user_input=user_input_text,
            retrieved_contexts=contexts,
            reference=reference_text
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


def get_reference_answer(region: str, timeframe: str, question_id: int) -> str:
    """
    Finds and joins all textual ground truth answers for a given region, timeframe, and question ID.
    """
    for entry in REFERENCE_DATA:
        if entry.get("region") == region and entry.get("timeframe") == timeframe:
            for q in entry.get("answers_per_question", []):
                if q.get("id") == question_id:
                    # Join multiple reference answers into a single string for RAGAS
                    answers = q.get("answers", [])
                    return "\n\n".join(answers) if answers else "no information found"

    return "no information found"