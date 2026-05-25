import pytest

from rag_project.core.config import get_settings


@pytest.fixture(autouse=True)
def isolated_env(tmp_path, monkeypatch):
    """Isolate storage per test to avoid duplicate carryover."""
    data = tmp_path / "data"
    indexes = data / "indexes"
    store = data / "store"
    for p in (data, indexes, store):
        p.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("DATA_DIR", str(data))
    monkeypatch.setenv("SQLITE_PATH", str(data / "metadata.db"))
    monkeypatch.setenv("FAISS_INDEX_PATH", str(indexes / "faiss.index"))
    monkeypatch.setenv("BM25_INDEX_PATH", str(indexes / "bm25"))
    monkeypatch.setenv("RAG_MIN_ANSWERABILITY_SCORE", "0.55")
    get_settings.cache_clear()
    from rag_project.services.factory import ServiceFactory

    ServiceFactory._instance = None
    yield
    ServiceFactory._instance = None
    get_settings.cache_clear()
