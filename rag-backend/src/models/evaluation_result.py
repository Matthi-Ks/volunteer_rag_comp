from pydantic import BaseModel

from models.enums import QuestionVariant

# todo add more metrics
class EvaluationResult(BaseModel):
    answer: str
    question_variant: QuestionVariant
    faithfulness: float
    answer_relevance: float