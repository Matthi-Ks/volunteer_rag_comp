from pydantic import BaseModel

from models.enums import RagPipeline, InformationTier

class PipelineSummary(BaseModel):
    pipeline_type: RagPipeline
    information_tier: InformationTier
    use_metadata_filter: bool
    use_esco_skills: bool
    total_runs: int
    avg_faithfulness: float
    avg_answer_relevancy: float
    avg_context_precision: float
    avg_context_recall: float
    avg_token_count: int