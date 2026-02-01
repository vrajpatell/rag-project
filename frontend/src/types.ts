export interface RAGRequest {
    query: string;
    top_k: number;
    use_rerank: boolean;
}

export interface ContextChunk {
    doc_id: number;
    section?: string | null;
    text: string;
    score: number;
    meta: Record<string, any>;
}

export interface RAGResponse {
    query: string;
    retrieved_contexts: ContextChunk[];
    synthesized_answer: string;
    confidence_score: number;
    citations: string[];
}
