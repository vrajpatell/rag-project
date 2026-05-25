from rag_project.retrieval.candidate_merger import merge_candidates


def test_merge_candidates():
    merged = merge_candidates([("a", 1.0), ("b", 0.5)], [("b", 2.0), ("c", 1.0)])
    assert "a" in merged and "b" in merged and "c" in merged
    assert merged["b"] >= merged.get("a", 0)
