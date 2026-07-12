from pydantic import BaseModel

from models.activity import ActivityMetadata
from models.enums import InformationTier, RagPipeline, QuestionVariant

class QueryOptions(BaseModel):
    informationTier: InformationTier
    pipeline: RagPipeline
    useMetadataFilter: bool

class Query(BaseModel):
    text_variants: dict[QuestionVariant, str]
    options: QueryOptions
    filter_values: ActivityMetadata | None

class QueryPacket(BaseModel):
    variants: dict[QuestionVariant, str]

class FusionRAGResponse(BaseModel):
    packets: list[dict[QuestionVariant, str]]


