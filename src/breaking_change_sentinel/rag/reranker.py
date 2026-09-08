"""
Module providing cross-encoder reranking capabilities using FlashRank.
"""

from typing import Any
from flashrank import Ranker, RerankRequest


class DocumentReranker:
    """
    Reranks candidate chunks retrieved from vector search using a cross-encoder model.
    """

    DEFAULT_MODEL: str = "ms-marco-TinyBERT-L-2-v2"

    def __init__(self, model_name: str = DEFAULT_MODEL) -> None:
        """
        Initializes the FlashRank Ranker instance.
        """
        self.model_name = model_name
        self._ranker = Ranker(model_name=self.model_name, cache_dir="/tmp/flashrank")

    def rerank(
        self,
        query: str,
        documents: list[dict[str, Any]],
        top_n: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Reranks a list of candidate document dictionaries based on query relevance.

        Args:
            query: The user query or search intent.
            documents: List of retrieved chunks containing 'content' and 'metadata'.
            top_n: Number of top-ranked documents to retain.

        Returns:
            The truncated list of documents sorted by descending relevance score.
        """

        if not documents:
            return []

        list_of_dicts = [
            {"id": x, "text": doc["content"]} for (x, doc) in enumerate(documents)
        ]

        reranked_result = self._ranker.rerank(
            RerankRequest(query=query, passages=list_of_dicts)
        )

        reranked_result_cut = reranked_result[:top_n]

        final_list = []

        for result in reranked_result_cut:
            doc_id = int(result["id"])
            shallow_doc = dict(documents[doc_id])
            shallow_doc["rerank_score"] = float(result["score"])
            final_list.append(shallow_doc)

        return final_list
