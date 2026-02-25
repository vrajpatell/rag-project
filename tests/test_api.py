from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_rag_endpoint():
    # Sending a query
    response = client.post(
        "/rag", json={"query": "What is RAG?", "top_k": 2, "use_rerank": False}
    )
    assert response.status_code == 200
    data = response.json()
    assert "synthesized_answer" in data
    assert "retrieved_contexts" in data
    # Note: len might be 2 if dummy index returns checks, or fewer.
    assert isinstance(data["retrieved_contexts"], list)


def test_rag_endpoint_with_rerank():
    response = client.post(
        "/rag", json={"query": "test", "top_k": 2, "use_rerank": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert "synthesized_answer" in data
