import type { Query, EvaluationResult, PipelineSummary } from "@/types/backendTypes";

const BASE_URL = "http://localhost:8080/api/"

export async function search_and_evaluate(query: Query): Promise<EvaluationResult[]>{
    try {
        const resp = await fetch(BASE_URL + 'search', {
            method: 'POST',
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(query)
        });
        return await handleResponse<EvaluationResult[]>(resp);
    } catch (error: any) {
        console.error("Error while fetching answer:", error.message);
        throw error;
    }
}

export async function get_pipeline_summaries() {
    try {
        const resp = await fetch(BASE_URL + 'summaries', {
            method: 'GET'
        });
        return await handleResponse<PipelineSummary[]>(resp);
    } catch (error: any) {
        console.error("Error while fetching summaries:", error.message);
        throw error;
    }
}

export async function mock_api_call(query: Query): Promise<EvaluationResult[]>{
    try {
        const resp = await fetch(BASE_URL + 'test', {
            method: 'POST',
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(query)
        });
        return await handleResponse<EvaluationResult[]>(resp);
    } catch (error: any) {
        console.error("Error while updating project:", error.message);
        throw error;
    }
}

async function handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
        let errorData: any = { message: 'Unknown Error' };
        try {
            errorData = await response.json();
        } catch (parseError) {
            errorData.message = response.statusText || 'Server responded with non-JSON error.';
        }
        const errorMessage = `HTTP error! Status: ${response.status} - ${errorData.message}`;
        throw new Error(errorMessage);
    }
    return await response.json() as T;
}