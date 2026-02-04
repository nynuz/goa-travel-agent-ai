from __future__ import annotations

import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PayloadSchemaType,
    PointStruct,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)
from tqdm import tqdm

from goa_travel_agent.config.settings import settings
from goa_travel_agent.src.embeddings.hybrid_embedder import HybridEmbedder
from goa_travel_agent.src.utils.logger import get_logger

log = get_logger(__name__)


class QdrantManager:
    """Manages Qdrant collections for hotels and places."""

    def __init__(self, url: str = "", api_key: str = "") -> None:
        qdrant_url = url or settings.QDRANT_URL
        qdrant_key = api_key or settings.QDRANT_API_KEY
        kwargs: dict = {"url": qdrant_url, "timeout": 30}
        if qdrant_key:
            kwargs["api_key"] = qdrant_key
        self.client = QdrantClient(**kwargs)

    # -- collection lifecycle --------------------------------------------

    def create_collection(self, name: str) -> None:
        self.client.recreate_collection(
            collection_name=name,
            vectors_config={"dense": VectorParams(size=settings.DENSE_DIM, distance=Distance.COSINE)},
            sparse_vectors_config={"sparse": SparseVectorParams()},
        )
        log.info("Created collection '%s'", name)

    def create_indexes(self, name: str) -> None:
        schemas: dict[str, PayloadSchemaType] = {
            "city": PayloadSchemaType.KEYWORD,
            "locality": PayloadSchemaType.TEXT,
            "hotel_star_rating": PayloadSchemaType.INTEGER,
            "site_review_rating": PayloadSchemaType.FLOAT,
            "category": PayloadSchemaType.KEYWORD,
        }
        for field, schema in schemas.items():
            try:
                self.client.create_payload_index(
                    collection_name=name, field_name=field, field_schema=schema,
                )
            except Exception:
                pass  # index may already exist
        log.info("Payload indexes created for '%s'", name)

    def collection_count(self, name: str) -> int:
        info = self.client.get_collection(name)
        return info.points_count or 0

    def collection_exists_and_populated(self, name: str) -> bool:
        try:
            return self.collection_count(name) > 0
        except Exception:
            return False

    # -- upload ----------------------------------------------------------

    def upload_points(
        self,
        name: str,
        dense_vectors: list[list[float]],
        sparse_data: list[tuple[list[int], list[float]]],
        payloads: list[dict],
        batch_size: int = 100,
    ) -> None:
        points: list[PointStruct] = []
        for i, (dense, (sp_idx, sp_val), payload) in enumerate(
            zip(dense_vectors, sparse_data, payloads)
        ):
            points.append(
                PointStruct(
                    id=i,
                    vector={
                        "dense": dense,
                        "sparse": SparseVector(indices=sp_idx, values=sp_val),
                    },
                    payload=payload,
                )
            )

        for start in tqdm(range(0, len(points), batch_size), desc=f"Uploading to '{name}'"):
            batch = points[start : start + batch_size]
            self.client.upsert(collection_name=name, points=batch)

        log.info("Uploaded %d points to '%s'", len(points), name)

    # -- high-level setup ------------------------------------------------

    @staticmethod
    def _sanitize_texts(texts: list) -> list[str]:
        return [str(t) if t is not None and t == t else "" for t in texts]

    def setup_hotels_collection(self, df: pd.DataFrame, embedder: HybridEmbedder) -> None:
        name = settings.HOTELS_COLLECTION
        self.create_collection(name)

        texts = self._sanitize_texts(df["search_text"].tolist())
        dense = embedder.encode_dense(texts).tolist()
        sparse = [embedder.encode_sparse(t) for t in tqdm(texts, desc="Sparse encoding hotels")]
        payloads = df.to_dict(orient="records")

        self.upload_points(name, dense, sparse, payloads)
        self.create_indexes(name)

    def setup_places_collection(self, df: pd.DataFrame, embedder: HybridEmbedder) -> None:
        name = settings.PLACES_COLLECTION
        self.create_collection(name)

        texts = self._sanitize_texts(df["full_text"].tolist())
        dense = embedder.encode_dense(texts).tolist()
        sparse = [embedder.encode_sparse(t) for t in tqdm(texts, desc="Sparse encoding places")]
        payloads = df.to_dict(orient="records")

        self.upload_points(name, dense, sparse, payloads)
        self.create_indexes(name)
