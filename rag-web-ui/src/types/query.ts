import type { InformationTier, QuestionVariant, RagPipeline, Region, TimeFrame } from "./enums";
import type Profile from "./profile";

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
    useMetadataFilter: boolean;
    useESCOSkills: boolean;
}

export interface RawQueryJson {
    id: number;
    text_variants: Record<QuestionVariant, string>;
}

export interface ActivityMetadata {
    region: Region,
    timeFrame: TimeFrame
}