"""Embedding worker CLI."""

import argparse

from rag_project.embeddings.batch_embedder import BatchEmbedder
from rag_project.services.factory import ServiceFactory


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection-id", default="default")
    parser.add_argument("--tenant-id", default="default")
    parser.add_argument("--batch-size", type=int, default=128)
    args = parser.parse_args()

    factory = ServiceFactory.get()
    chunks = []
    for doc in factory.document_store.list_documents(args.tenant_id, args.collection_id):
        chunks.extend(
            factory.document_store.get_chunks_by_document(doc.document_id, args.tenant_id)
        )
    embedder = BatchEmbedder(factory.embedding_provider, batch_size=args.batch_size)
    result = embedder.embed_chunks(chunks)
    print(f"Embedded {len(result)} chunks")


if __name__ == "__main__":
    main()
