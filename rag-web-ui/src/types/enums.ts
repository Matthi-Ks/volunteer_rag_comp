
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