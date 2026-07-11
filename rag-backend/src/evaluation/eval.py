import os

from mistralai import Mistral
from ragas import experiment
from ragas.metrics.collections import Faithfulness, AnswerRelevancy
from ragas.llms import llm_factory

from models.evaluation_result import EvaluationResult
from models.query import Query
from pipelines.rag_base import RagBase

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
llm = llm_factory("mistral-large",provider="mistral", client=client)

@experiment()
async def evaluate(query: Query, pipeline: RagBase) -> list[EvaluationResult]:

    answers = pipeline.execute_pipeline(query)

    faithfulness_scorer = Faithfulness(llm=llm)
    answer_relevancy_scorer = AnswerRelevancy(llm=llm)

    eval_results: list[EvaluationResult] = []
    for answer in answers:
        faithfulness = await faithfulness_scorer.ascore(
            response=answer.model_response,
            user_input=query.text_variants.get(answer.questionVariant),
            retrieved_contexts=answer.used_context
        )
        answer_relevancy = await answer_relevancy_scorer.ascore(
            response=answer.model_response,
            user_input=query.text_variants.get(answer.questionVariant),
        )

        eval_results.append(EvaluationResult(
            answer=answer.model_response,
            question_variant=answer.questionVariant,
            faithfulness=faithfulness.value,
            answer_relevance=answer_relevancy.value,
        ))

    return eval_results


