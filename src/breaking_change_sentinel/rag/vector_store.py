"""
Module for managing the Qdrant vector database and document embeddings.
"""

from typing import Any

from qdrant_client import QdrantClient, models
from fastembed import SparseTextEmbedding, TextEmbedding
import uuid


class MigrationVectorStore:
    """
    Manages the ingestion and hybrid retrieval (Dense + Sparse BM25) of migration documentation.
    """

    DEFAULT_DENSE_MODEL: str = "BAAI/bge-small-en"
    DEFAULT_SPARSE_MODEL: str = "Qdrant/bm25"
    DENSE_VECTOR_NAME: str = "dense"
    SPARSE_VECTOR_NAME: str = "sparse"

    def __init__(
        self,
        collection_name: str = "migration_docs",
        location: str = ":memory:",
        dense_model: str = DEFAULT_DENSE_MODEL,
        sparse_model: str = DEFAULT_SPARSE_MODEL,
    ) -> None:
        """
        Initializes the vector store client and configures collection names and models.
        """
        self.collection_name = collection_name
        self.dense_model = dense_model
        self.sparse_model = sparse_model
        self.client = QdrantClient(location)

        self._dense_embedder = TextEmbedding()
        self._sparse_embedder = SparseTextEmbedding(model_name=self.sparse_model)

        self._ensure_collection_exists()

    def _ensure_collection_exists(self) -> None:
        """
        Creates the collection with named dense and sparse vector spaces if missing.
        """

        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config={
                    self.DENSE_VECTOR_NAME: models.VectorParams(
                        size=self.client.get_embedding_size(self.dense_model),
                        distance=models.Distance.COSINE,
                    )
                },
                sparse_vectors_config={
                    self.SPARSE_VECTOR_NAME: models.SparseVectorParams()
                },
            )

    def index_chunks(self, chunks: list[dict[str, Any]]) -> None:
        """
        Embeds and stores the markdown chunks into Qdrant using upload_collection.

        Args:
                chunks: List of dictionaries containing 'content' and 'metadata'.
        """
        if not chunks:
            return

        list_of_content = [doc["content"] for doc in chunks]

        dense_embedding = self._dense_embedder.embed(list_of_content)
        sparse_embedding = self._sparse_embedder.embed(list_of_content)

        points: list[models.PointStruct] = []
        for chunk, dense_emb, sparse_emb in zip(
            chunks, dense_embedding, sparse_embedding
        ):
            points.append(
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    payload=chunk,
                    vector={
                        self.DENSE_VECTOR_NAME: dense_emb.tolist(),
                        self.SPARSE_VECTOR_NAME: models.SparseVector(
                            indices=sparse_emb.indices.tolist(),
                            values=sparse_emb.values.tolist(),
                        ),
                    },
                )
            )

        self.client.upsert(collection_name=self.collection_name, points=points)

    def search(self, query: str, limit: int = 3) -> list[dict[str, Any]]:
        """
        Executes a hybrid search combining dense and sparse vectors via Reciprocal Rank Fusion.

        Args:
            query: The search query string.
            limit: Maximum number of relevant chunks to return.

        Returns:
            A list of dictionaries containing 'content' and 'metadata'.
        """

        dense_query = models.Document(text=query, model=self.dense_model)
        sparse_query = models.Document(text=query, model=self.sparse_model)

        prefetch = [
            models.Prefetch(
                query=dense_query, using=self.DENSE_VECTOR_NAME, limit=limit * 2
            ),
            models.Prefetch(
                query=sparse_query, using=self.SPARSE_VECTOR_NAME, limit=limit * 2
            ),
        ]

        search_result = self.client.query_points(
            collection_name=self.collection_name,
            prefetch=prefetch,
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=limit,
        )

        hits = [hit.payload for hit in search_result.points if hit.payload is not None]

        return hits
