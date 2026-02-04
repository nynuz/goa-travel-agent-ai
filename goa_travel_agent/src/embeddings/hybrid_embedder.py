from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

from goa_travel_agent.config.settings import settings
from goa_travel_agent.src.utils.logger import get_logger

log = get_logger(__name__)


class HybridEmbedder:
    """Produces dense (SentenceTransformer) and sparse (TF-IDF) vectors.

    CRITICAL FIX: TF-IDF is fitted ONCE on the full corpus and reused
    via ``transform()`` only, so all sparse vectors share the same vocabulary.
    """

    def __init__(
        self,
        dense_model_name: str = settings.DENSE_MODEL_NAME,
        tfidf_path: Path = settings.TFIDF_PATH,
    ) -> None:
        self._dense_model_name = dense_model_name
        self._tfidf_path = tfidf_path
        self._dense_model: SentenceTransformer | None = None
        self._tfidf: TfidfVectorizer | None = None

    # -- dense -----------------------------------------------------------

    @property
    def dense_model(self) -> SentenceTransformer:
        if self._dense_model is None:
            log.info("Loading dense model '%s'...", self._dense_model_name)
            self._dense_model = SentenceTransformer(self._dense_model_name)
        return self._dense_model

    def encode_dense(self, texts: list[str], batch_size: int = 64) -> np.ndarray:
        """Batch-encode texts to dense vectors (N x 384)."""
        return self.dense_model.encode(
            texts, batch_size=batch_size, show_progress_bar=True, normalize_embeddings=True,
        )

    # -- sparse (TF-IDF) -------------------------------------------------

    @property
    def tfidf(self) -> TfidfVectorizer:
        if self._tfidf is None:
            if self._tfidf_path.exists():
                self.load_tfidf()
            else:
                raise RuntimeError(
                    "TF-IDF model not found. Call fit_tfidf(corpus) first."
                )
        return self._tfidf  # type: ignore[return-value]

    def fit_tfidf(self, corpus: list[str]) -> None:
        """Fit TF-IDF on the ENTIRE corpus (hotels + places) and persist."""
        # Sanitize: replace NaN/None with empty string, ensure all are str
        corpus = [str(doc) if doc is not None and doc == doc else "" for doc in corpus]
        corpus = [doc for doc in corpus if doc.strip()]
        log.info("Fitting TF-IDF on %d documents...", len(corpus))
        self._tfidf = TfidfVectorizer()
        self._tfidf.fit(corpus)
        self._tfidf_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._tfidf, self._tfidf_path)
        log.info("TF-IDF model saved to %s (vocab size: %d)", self._tfidf_path, len(self._tfidf.vocabulary_))

    def load_tfidf(self) -> None:
        """Load a previously fitted TF-IDF model."""
        log.info("Loading TF-IDF model from %s", self._tfidf_path)
        self._tfidf = joblib.load(self._tfidf_path)

    def encode_sparse(self, text: str) -> tuple[list[int], list[float]]:
        """Transform a SINGLE text to sparse vector (indices, values).

        Never calls fit — only transform on the already-fitted model.
        """
        row = self.tfidf.transform([text])
        return row.indices.tolist(), row.data.tolist()

    def is_tfidf_fitted(self) -> bool:
        return self._tfidf_path.exists()
