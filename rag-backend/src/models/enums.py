from enum import Enum

class InformationTier(Enum):
    TITLE_ONLY = "title_only"
    TITLE_SOFTSKILL = "title_softskill" # activity title only with associated softskills
    TITLE_DESC = "title_desc" # all activty cols
    TITLE_DESC_SOFTSKILL = "title_desc_softskill" # all activity cols with associated softskills

class RagPipeline(Enum):
    HYBRID = "hybrid"
    GRAPH = "graph"
    FUSION = "fusion"


class QuestionVariant(Enum):
    NORMAL = "normal"
    ABSTRACT = "abstract"
    DETAILED = "detailed"
