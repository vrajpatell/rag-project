"""Indexing worker CLI."""

from __future__ import annotations

import argparse

from rag_project.services.factory import ServiceFactory


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection-id", default="default")
    parser.add_argument("--tenant-id", default="default")
    parser.add_argument("--mode", choices=["incremental", "rebuild"], default="incremental")
    args = parser.parse_args()

    factory = ServiceFactory.get()
    docs = factory.document_store.list_documents(args.tenant_id, args.collection_id)
    all_chunks = []
    for doc in docs:
        all_chunks.extend(
            factory.document_store.get_chunks_by_document(doc.document_id, args.tenant_id)
        )
    if not all_chunks:
        print("No chunks to index")
        return
    result = factory.hybrid_indexer.index_chunks(all_chunks, mode=args.mode)
    factory.hybrid_indexer.persist(
        factory.settings.bm25_index_path,
        factory.settings.faiss_index_path,
    )
    print(f"Indexed {result.get('indexed', 0)} chunks")


if __name__ == "__main__":
    main()
