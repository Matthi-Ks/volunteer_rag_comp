import math

from pydantic import BaseModel, field_validator

from models.enums import QuestionVariant

# todo add more metrics
class EvaluationResult(BaseModel):
    answer: str
    question_variant: QuestionVariant
    faithfulness: float = 0.0
    answer_relevance: float = 0.0
    token_count: int
    context_recall: float = 0.0
    context_precision: float = 0.0
    context: list[str]
    matching_skills: list[str]

    @field_validator("faithfulness", "answer_relevance", "context_precision", "context_recall", mode="before")
    @classmethod
    def sanitize_nan(cls, v):
        if isinstance(v, float) and math.isnan(v):
            return 0.0  # Or return None if your model allows optional floats
        return v