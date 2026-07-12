from pydantic import BaseModel

from models.enums import QuestionVariant


class PipelineResult(BaseModel):
    used_context: list[str]
    model_response: str
    questionVariant: QuestionVariant
    tokens_used: int