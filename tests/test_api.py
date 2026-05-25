from fastapi.testclient import TestClient
from rag_project.api.app import app

client = TestClient(app)


def test_health_live():
    r = client.get("/health/live")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_rag_v1_schema():
    r = client.post(
        "/api/v1/rag/query",
        json={"query": "test query", "allow_abstention": True},
    )
    assert r.status_code == 200
    data = r.json()
    assert "answer" in data
    assert "trace_id" in data
    assert "confidence_score" in data
