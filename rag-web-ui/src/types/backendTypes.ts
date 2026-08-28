
export enum QuestionVariant {
    NORMAL = "normal",
    ABSTRACT = "abstract",
    DETAILED = "detailed"
}

export enum InformationTier {
    TITLE_ONLY = "title_only",
    TITLE_DESC = "title_desc",
    MaT_TITLE_ONLY = "mat_title_only",
    MaT_TITLE_DESC = "mat_title_desc",
}

export enum RagPipeline {
    HYBRID = "hybrid",
    GRAPH = "graph",
    FUSION = "fusion"
}

export enum Region {
    NORCAL = "Northern California",
    SOCAL = "Southern California",
    OUT_OF_STATE = "Outside California",
    REMOTE = "Remote"
}

export enum TimeFrame {
    ASAP = "As soon as possible",
    SUMMER = "Starting during summer",
    WINTER = "Starting during winter"
}

export interface EvaluationResult {
    answer: String;
    question_variant: QuestionVariant;
    faithfulness: number;
    answer_relevance: number;
    token_count: number;
    context_recall: number;
    context_precision: number;
    context: string[];
    matching_skills: string[];
}

export interface PipelineSummary {
    pipeline_type: RagPipeline,
    information_tier: InformationTier,
    use_Mat: boolean,
    use_esco_skills: boolean,
    total_runs: number,
    avg_faithfulness: number,
    avg_answer_relevancy: number,
    avg_context_precision: number,
    avg_context_recall: number,
    avg_token_count: number,
}

export interface Profile {
    id: number,
    esco_skills: string[],
    biography: string
}

export interface Query {
    profile: Profile,
    query_id: number,
    text_variants: Record<QuestionVariant, string>
    options: QueryOptions
    filter_values: ActivityMetadata
}

export interface QueryOptions {
    informationTier: InformationTier;
    pipeline: RagPipeline;
    useMaT: boolean;
    useESCOSkills: boolean;
}

export interface ActivityMetadata {
    region: Region,
    timeFrame: TimeFrame
}