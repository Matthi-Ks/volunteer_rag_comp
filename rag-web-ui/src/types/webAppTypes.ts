import type { EvaluationResult, QuestionVariant } from "./backendTypes";

export interface ChatMessage {
    id: number;
    sender: "user" | "system";
    text: string;
    results?: EvaluationResult[];
    matchingResult?: EvaluationResult;
    textVariants?: Record<QuestionVariant, string>;
    activeVariantIndex?: number;
}

export interface PickerItem {
   rawTextTemplate: string;
   displayText: string;
   variantType: QuestionVariant;
   parentQuery: RawQueryJson;
}

export interface RawQueryJson {
    id: number;
    text_variants: Record<QuestionVariant, string>;
}