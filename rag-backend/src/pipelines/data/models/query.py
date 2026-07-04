from enum import Enum

from pydantic import BaseModel

from pipelines.data.models.activity import ActivityMetadata


class InformationTier(Enum):
    TITLE_ONLY = "title_only"
    TITLE_SOFTSKILL = "title_softskill"
    TITLE_DESC = "title_desc"
    TITLE_DESC_SOFTSKILL = "title_desc_softskill"

class RAGPipeline(Enum):
    HYBRID = "hybrid"
    GRAPH = "graph"
    FUSION = "fusion"

class QueryOptions(BaseModel):
    informationTier: InformationTier
    pipeline: RAGPipeline
    useMetadataFilter: bool

class Query(BaseModel):
    text: str
    options: QueryOptions
    filter_values: ActivityMetadata


