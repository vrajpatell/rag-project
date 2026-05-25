from rag_project.cache.memory_cache import MemoryCache


def test_tenant_cache_isolation():
    cache = MemoryCache()
    cache.set_query_response("t1", ["c1"], "query", {}, {"answer": "a1"})
    cache.set_query_response("t2", ["c1"], "query", {}, {"answer": "a2"})
    assert cache.get_query_response("t1", ["c1"], "query", {})["answer"] == "a1"
    assert cache.get_query_response("t2", ["c1"], "query", {})["answer"] == "a2"
