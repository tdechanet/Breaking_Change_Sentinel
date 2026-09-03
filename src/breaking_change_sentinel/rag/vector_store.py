"""
Module for managing the Qdrant vector database and document embeddings.
"""

from typing import Any

from qdrant_client import QdrantClient, models


class MigrationVectorStore:
    """
    Manages the ingestion and retrieval of migration documentation chunks.
    """

    DEFAULT_MODEL: str = "BAAI/bge-small-en"

    def __init__(
        self,
        collection_name: str = "migration_docs",
        location: str = ":memory:",
        model_name: str = DEFAULT_MODEL,
    ) -> None:
        """
        Initializes the Qdrant client. Uses in-memory storage by default for local dev.
        """
        self.collection_name = collection_name
        self.model_name = model_name
        self.client = QdrantClient(location)

        self._ensure_collection_exists()

    def _ensure_collection_exists(self) -> None:
        """
        Creates the collection if it does not already exist.
        """

        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.client.get_embedding_size(self.model_name),
                    distance=models.Distance.COSINE,
                ),
            )

    def index_chunks(self, chunks: list[dict[str, Any]]) -> None:
        """
        Embeds and stores the markdown chunks into Qdrant using upload_collection.

        Args:
            chunks: List of dictionaries containing 'content' and 'metadata'.
        """
        if not chunks:
            return

        chunks_ids = list(range(len(chunks)))  # Attribute an id to each chunk

        doc_list = [
            models.Document(text=chunk["content"], model=self.model_name)
            for chunk in chunks
        ]

        self.client.upload_collection(
            self.collection_name, vectors=doc_list, payload=chunks, ids=chunks_ids
        )

    def search(self, query: str, limit: int = 3) -> list[dict[str, Any]]:
        """
        Searches the vector store using semantic query matching.

        Args:
            query: The search query string.
            limit: Maximum number of results to return.

        Returns:
            A list of dictionaries containing 'content' and 'metadata'.
        """
        # TODO: Call self.client.query_points() with:
        # collection_name=self.collection_name,
        # query=models.Document(text=query, model=self.model_name),
        # limit=limit

        # TODO: Extract and return [{"content": hit.payload["content"], "metadata": hit.payload["metadata"]} for hit in results.points]
        return []
