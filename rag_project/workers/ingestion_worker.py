"""Ingestion worker CLI."""

import argparse

from rag_project.ingestion.pipeline import IngestionPipeline
from rag_project.services.factory import ServiceFactory


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--tenant-id", default="default")
    parser.add_argument("--collection-id", default="default")
    args = parser.parse_args()

    factory = ServiceFactory.get()
    pipeline = IngestionPipeline(factory.document_store, factory.metadata_store)
    summary, chunks = pipeline.ingest_local(args.source, args.tenant_id, args.collection_id)
    if chunks:
        factory.hybrid_indexer.index_chunks(chunks)
        factory.hybrid_indexer.persist(
            factory.settings.bm25_index_path,
            factory.settings.faiss_index_path,
        )
    print(summary)


if __name__ == "__main__":
    main()
