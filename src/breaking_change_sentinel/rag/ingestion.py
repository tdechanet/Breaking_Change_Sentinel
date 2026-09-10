"""
Module orchestrating the ingestion of migration documentation into the vector store.
"""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from breaking_change_sentinel.rag.chunker import chunk_markdown_documentation
from breaking_change_sentinel.rag.vector_store import MigrationVectorStore

ChunkerFunc = Callable[[str], list[dict[str, Any]]]


class DocumentationIngestionPipeline:
    """
    Coordinates markdown file discovery, hierarchical chunking,
    metadata enrichment, and storage in Qdrant.
    """

    def __init__(
        self,
        vector_store: MigrationVectorStore,
        chunker: ChunkerFunc = chunk_markdown_documentation,
    ) -> None:
        """
        Initializes the ingestion pipeline with an active vector store and chunking callable.
        """
        self.vector_store = vector_store
        self._chunker = chunker

    def ingest_file(self, file_path: Path) -> int:
        """
        Reads a single markdown file, chunks it, enriches metadata,
        and loads it into the vector store.

        Args:
                        file_path: Absolute or relative Path instance pointing to a .md file.

        Returns:
                        The number of chunks indexed from this file.
        """

        if not file_path.is_file() or file_path.suffix != ".md":
            return 0

        try:
            file_content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return 0

        if not file_content.strip():
            return 0

        chunks = self._chunker(file_content)
        if not chunks:
            return 0

        file_metadata = {
            "source_file": file_path.name,
            "file_path": str(file_path.resolve()),
        }

        for chunk in chunks:
            chunk.setdefault("metadata", {}).update(file_metadata)

        self.vector_store.index_chunks(chunks)
        return len(chunks)

    def ingest_directory(self, directory_path: Path) -> int:
        """
        Recursively scans a directory for all markdown files and ingests them.

        Args:
                        directory_path: Directory path containing documentation files.

        Returns:
                        Total count of chunks indexed across all discovered files.
        """

        if not directory_path.is_dir():
            return 0

        counter = 0
        for file in sorted(directory_path.rglob("*.md")):
            counter += self.ingest_file(file)

        return counter
