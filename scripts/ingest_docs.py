"""
CLI entrypoint to ingest markdown migration documentation into persistent local Qdrant storage.
"""

import argparse
import logging
from pathlib import Path
import sys

from breaking_change_sentinel.rag.ingestion import DocumentationIngestionPipeline
from breaking_change_sentinel.rag.vector_store import MigrationVectorStore

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s"
)
logger = logging.getLogger(__name__)


def run_ingestion(docs_dir: Path, storage_path: Path) -> int:
    """
    Ingests all markdown documents from docs_dir into a persistent Qdrant collection.

    Args:
        docs_dir: Directory containing source markdown migration files.
        storage_path: Local directory where Qdrant persists its vector index.

    Returns:
        Total number of chunks successfully indexed.

    Raises:
        FileNotFoundError: If docs_dir does not exist or is not a directory.
    """

    if not docs_dir.is_dir():
        raise FileNotFoundError(f"Source directory does not exist: {docs_dir}")

    storage_path.mkdir(parents=True, exist_ok=True)

    vec_store = MigrationVectorStore(path=storage_path)

    doc_ingest_pipe = DocumentationIngestionPipeline(vec_store)

    chunk_count = doc_ingest_pipe.ingest_directory(docs_dir)

    return chunk_count


def main() -> None:
    """Parses command-line arguments and triggers documentation ingestion."""
    parser = argparse.ArgumentParser(
        description="Ingest migration markdown documents into local Qdrant."
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=Path("data/migration_docs"),
        help="Source directory containing markdown documentation (default: data/migration_docs)",
    )
    parser.add_argument(
        "--storage-path",
        type=Path,
        default=Path("data/qdrant_storage"),
        help="Local directory for Qdrant persistence (default: data/qdrant_storage)",
    )

    args = parser.parse_args()

    try:
        total_chunks = run_ingestion(
            docs_dir=args.docs_dir, storage_path=args.storage_path
        )
        logger.info(
            "Ingestion finished successfully: %d chunks stored in '%s'",
            total_chunks,
            args.storage_path,
        )
    except FileNotFoundError as exc:
        logger.error("Configuration error: %s", exc)
        sys.exit(1)
    except Exception as exc:
        logger.exception("Unexpected error during ingestion: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
