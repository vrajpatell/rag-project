from rag_project.core.hashing import SimHash, content_hash


def test_content_hash_stable():
    h1 = content_hash("Hello  World")
    h2 = content_hash("hello world")
    assert h1 == h2


def test_simhash_identical_text():
    sh = SimHash()
    text = "refund policy thirty days receipt purchase"
    assert sh.fingerprint(text) == sh.fingerprint(text)
