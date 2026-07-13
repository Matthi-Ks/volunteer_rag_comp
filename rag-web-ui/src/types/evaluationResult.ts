import type { QuestionVariant } from "./enums"

export interface EvaluationResult {
    answer: String
    question_variant: QuestionVariant
    faithfulness: number
    answer_relevance: number
    token_count: number
    context_recall: number
    context_precision: number
}

