from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchText,
    MatchValue,
    Range,
    SparseVector,
)
from sentence_transformers import CrossEncoder

from goa_travel_agent.config.settings import settings
from goa_travel_agent.src.embeddings.hybrid_embedder import HybridEmbedder
from goa_travel_agent.src.utils.logger import get_logger

log = get_logger(__name__)


def _rrf(ranked_lists: list[list[int]], k: int = 60) -> list[int]:
    """Reciprocal Rank Fusion over multiple ranked id-lists."""
    scores: dict[int, float] = {}
    for rlist in ranked_lists:
        for rank, doc_id in enumerate(rlist, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return [doc_id for doc_id, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)]


class HybridSearcher:
    """Hybrid (dense + sparse) search with RRF fusion and cross-encoder reranking."""

    def __init__(
        self,
        embedder: HybridEmbedder,
        qdrant_client: QdrantClient | None = None,
    ) -> None:
        self.embedder = embedder
        if qdrant_client:
            self.client = qdrant_client
        else:
            kwargs: dict = {"url": settings.QDRANT_URL, "timeout": 30}
            if settings.QDRANT_API_KEY:
                kwargs["api_key"] = settings.QDRANT_API_KEY
            self.client = QdrantClient(**kwargs)
        self._reranker: CrossEncoder | None = None

    @property
    def reranker(self) -> CrossEncoder:
        if self._reranker is None:
            log.info("Loading cross-encoder reranker...")
            self._reranker = CrossEncoder(settings.CROSS_ENCODER_NAME)
        return self._reranker

    # -- core search -----------------------------------------------------

    def _search(
        self,
        collection: str,
        query: str,
        filters: Filter | None,
        retrieve_limit: int = 20,
        top_k: int = 5,
        text_field: str = "search_text",
    ) -> list[dict]:
        # encode query
        q_dense = self.embedder.encode_dense([query])[0].tolist()
        sp_idx, sp_val = self.embedder.encode_sparse(query)

        # dense search via query_points (qdrant-client >= 1.12)
        dense_resp = self.client.query_points(
            collection_name=collection,
            query=q_dense,
            using="dense",
            query_filter=filters,
            limit=retrieve_limit,
            with_payload=False,
        )
        dense_hits = dense_resp.points

        # sparse search via query_points
        sparse_resp = self.client.query_points(
            collection_name=collection,
            query=SparseVector(indices=sp_idx, values=sp_val),
            using="sparse",
            query_filter=filters,
            limit=retrieve_limit,
            with_payload=False,
        )
        sparse_hits = sparse_resp.points

        # RRF fusion
        dense_ids = [h.id for h in dense_hits]
        sparse_ids = [h.id for h in sparse_hits]
        fused_ids = _rrf([dense_ids, sparse_ids])

        if not fused_ids:
            return []

        # retrieve full payloads
        records = self.client.retrieve(collection, ids=fused_ids, with_payload=True)
        id_to_payload = {r.id: r.payload for r in records}

        candidates = []
        for pid in fused_ids:
            payload = id_to_payload.get(pid)
            if payload:
                candidates.append({"id": pid, **payload})

        if not candidates:
            return []

        # rerank
        passages = [str(c.get(text_field, "") or "") for c in candidates]
        pairs = [(query, p) for p in passages]
        scores = self.reranker.predict(pairs)
        for c, s in zip(candidates, scores):
            c["rerank_score"] = float(s)

        candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
        return candidates[:top_k]

    # -- public API ------------------------------------------------------

    def search_hotels(
        self,
        query: str,
        min_stars: float = 0,
        min_rating: float = 0,
        locality: str | None = None,
        top_k: int = 5,
    ) -> list[dict]:
        must_conditions: list = []
        if min_stars > 0:
            must_conditions.append(
                FieldCondition(key="hotel_star_rating", range=Range(gte=min_stars))
            )
        if min_rating > 0:
            must_conditions.append(
                FieldCondition(key="site_review_rating", range=Range(gte=min_rating))
            )
        if locality:
            must_conditions.append(
                FieldCondition(key="locality", match=MatchText(text=locality))
            )

        qfilter = Filter(must=must_conditions) if must_conditions else None
        return self._search(
            collection=settings.HOTELS_COLLECTION,
            query=query,
            filters=qfilter,
            top_k=top_k,
            text_field="search_text",
        )

    def search_places(
        self,
        query: str,
        category: str | None = None,
        top_k: int = 5,
    ) -> list[dict]:
        must_conditions: list = []
        if category:
            must_conditions.append(
                FieldCondition(key="category", match=MatchValue(value=category))
            )

        qfilter = Filter(must=must_conditions) if must_conditions else None
        return self._search(
            collection=settings.PLACES_COLLECTION,
            query=query,
            filters=qfilter,
            top_k=top_k,
            text_field="full_text",
        )
