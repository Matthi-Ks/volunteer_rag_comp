from enum import Enum

class InformationTier(Enum):
    TITLE_ONLY = "title_only"
    TITLE_DESC = "title_desc"
    # use metadata as text for embeddings
    MaT_TITLE_ONLY = "mat_title_only"
    MaT_TITLE_DESC = "mat_title_desc"

class RagPipeline(Enum):
    HYBRID = "hybrid"
    GRAPH = "graph"
    FUSION = "fusion"

class QuestionVariant(Enum):
    NORMAL = "normal"
    ABSTRACT = "abstract"
    DETAILED = "detailed"

