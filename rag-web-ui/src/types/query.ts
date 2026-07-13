import type { InformationTier, QuestionVariant, RagPipeline } from "./enums";

export interface Query {
    text_variants: Record<QuestionVariant, string>
    options: QueryOptions
    filter_values: ActivityMetadata
}

export interface QueryOptions {
    informationTier: InformationTier;
    pipeline: RagPipeline;
    useMetadataFilter: boolean;
}

export interface RawQueryJson {
    id: number;
    reference_answer: string;
    text_variants: Record<QuestionVariant, string>;
}

export interface ActivityMetadata {
    location: string,
    starting_date: string,
    end_date: string | null
}