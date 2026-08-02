from pydantic import BaseModel

from models.enums import QuestionVariant

# todo add more metrics
class EvaluationResult(BaseModel):
    answer: str
    question_variant: QuestionVariant
    faithfulness: float
    answer_relevance: float
    token_count: int
    context_recall: float
    context_precision: float
    context: list[str]
    matching_skills: list[str]