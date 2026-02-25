"""Generate an answer given retrieved contexts."""

import os
from typing import List, Dict, Any

try:
    import openai
except ImportError:
    openai = None


def synthesize_answer(query: str, contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Combine the query and contexts to produce an answer.

    If OPENAI_API_KEY is set, uses OpenAI API. Otherwise returns a dummy answer.
    """
    api_key = os.environ.get("OPENAI_API_KEY")

    if api_key and openai:
        try:
            client = openai.OpenAI(api_key=api_key)

            context_text = "\n\n".join(
                [f"Document {c['doc_id']}: {c['text']}" for c in contexts]
            )
            prompt = (
                "Answer the query based on the context below.\n\n"
                f"Context:\n{context_text}\n\n"
                f"Query: {query}\n\nAnswer:"
            )

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            answer = response.choices[0].message.content
            confidence = 1.0  # Placeholder, as API doesn't return confidence easily

            citations = [f"[{ctx['doc_id']}]" for ctx in contexts]

            return {
                "query": query,
                "retrieved_contexts": contexts,
                "synthesized_answer": answer,
                "confidence_score": confidence,
                "citations": citations,
            }
        except Exception as e:
            # Fallback if API fails
            print(f"OpenAI API failed: {e}")
            pass

    # Fallback / Stub
    citations = [f"[{ctx['doc_id']}]" for ctx in contexts]
    answer = f"Answer to '{query}' citing {', '.join(citations)}."
    confidence = 0.5  # dummy confidence score
    return {
        "query": query,
        "retrieved_contexts": contexts,
        "synthesized_answer": answer,
        "confidence_score": confidence,
        "citations": citations,
    }
