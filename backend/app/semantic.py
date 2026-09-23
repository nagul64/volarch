"""Semantic matching layer with graceful degradation.

Pick the strongest engine the environment allows:
  1. Gemini Embeddings API   -> set GEMINI_API_KEY (Google AI Studio)
  2. OpenAI Embeddings API   -> set OPENAI_API_KEY (or OPENAI_BASE_URL for
                                local OpenAI-compatible servers)
  3. sentence-transformers   -> `pip install sentence-transformers`
  4. Built-in TF-IDF         -> stdlib only, always works offline

Whatever is active, the public interface is the same:
    scorer.fit(corpus_texts)      # optional prep (TF-IDF needs it)
    scorer.similarity(a, b)       # float 0..1
    scorer.provider               # human-readable name
"""
from __future__ import annotations

import math
import os
import re
from collections import Counter

try:
    from sentence_transformers import SentenceTransformer
    _HAS_SENTENCE_TRANSFORMERS = True
except Exception:  # pragma: no cover - import guard
    _HAS_SENTENCE_TRANSFORMERS = False

STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "for", "to", "in", "on", "at",
    "with", "who", "that", "this", "these", "those", "it", "is", "are",
    "was", "were", "be", "been", "has", "have", "had", "she", "he", "her",
    "his", "their", "they", "them", "i", "you", "we", "our", "us",
}

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN_RE.findall(text.lower()) if t not in STOPWORDS]


# ---------------------------------------------------------------------------
# TF-IDF implementation (stdlib only)
# ---------------------------------------------------------------------------

class TfidfScorer:
    """Classic Information-Retrieval similarity, no dependencies.

    TF-IDF = how rare+important words are. Words that appear often in one
    text but rarely across the corpus get high weight.
    """

    def __init__(self) -> None:
        self._idf: dict[str, float] = {}
        self._ready = False

    @property
    def provider(self) -> str:
        return "tfidf (built-in)"

    def fit(self, texts: list[str]) -> None:
        tokenized = [set(_tokenize(t)) for t in texts]
        n_docs = len(tokenized)
        df: Counter[str] = Counter()
        for tokens in tokenized:
            df.update(tokens)
        self._idf = {
            term: math.log((1 + n_docs) / (1 + count)) + 1
            for term, count in df.items()
        }
        self._ready = n_docs > 0

    def _vector(self, text: str) -> dict[str, float]:
        tf = Counter(_tokenize(text))
        total = sum(tf.values()) or 1
        return {
            term: (count / total) * self._idf.get(term, 1.0)
            for term, count in tf.items()
        }

    @staticmethod
    def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
        common = set(a) & set(b)
        dot = sum(a[t] * b[t] for t in common)
        mag_a = math.sqrt(sum(v * v for v in a.values())) or 1.0
        mag_b = math.sqrt(sum(v * v for v in b.values())) or 1.0
        return dot / (mag_a * mag_b)

    def similarity(self, a: str, b: str) -> float:
        if not self._ready:
            self.fit([a, b])
        vec_a, vec_b = self._vector(a), self._vector(b)
        sim = self._cosine(vec_a, vec_b)
        return max(0.0, min(1.0, sim))


# ---------------------------------------------------------------------------
# sentence-transformers (local neural embeddings)
# ---------------------------------------------------------------------------

class SentenceTransformerScorer:
    def __init__(self) -> None:
        self._model: SentenceTransformer | None = None

    @property
    def provider(self) -> str:
        return "sentence-transformers (local neural)"

    def fit(self, texts: list[str]) -> None:
        pass  # nothing needed

    def _get_model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
        return self._model

    def similarity(self, a: str, b: str) -> float:
        model = self._get_model()
        [va, vb] = model.encode([a, b], normalize_embeddings=True)
        return max(0.0, min(1.0, float(va @ vb)))


# ---------------------------------------------------------------------------
# OpenAI (or OpenAI-compatible) embeddings
# ---------------------------------------------------------------------------

class OpenAIEmbeddingsScorer:
    def __init__(self) -> None:
        from openai import OpenAI  # noqa: WPS433 - lazy import on purpose

        self._client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY") or "ollama",
            base_url=os.getenv("OPENAI_BASE_URL") or None,
        )
        self._model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    @property
    def provider(self) -> str:
        base = os.getenv("OPENAI_BASE_URL")
        return f"openai embeddings ({self._model})" if not base \
            else f"openai-compatible embeddings ({self._model})"

    def fit(self, texts: list[str]) -> None:
        pass

    def similarity(self, a: str, b: str) -> float:
        resp = self._client.embeddings.create(model=self._model, input=[a, b])
        va, vb = resp.data[0].embedding, resp.data[1].embedding
        return max(0.0, min(1.0, float(dot(va, vb))))


# ---------------------------------------------------------------------------
# Gemini embeddings (Google AI Studio)
# ---------------------------------------------------------------------------

class GeminiEmbeddingsScorer:
    def __init__(self) -> None:
        from google import genai  # noqa: WPS433 - lazy import on purpose

        self._client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self._model = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")

    @property
    def provider(self) -> str:
        return f"gemini embeddings ({self._model})"

    def fit(self, texts: list[str]) -> None:
        pass

    def similarity(self, a: str, b: str) -> float:
        resp = self._client.models.embed_content(
            model=self._model, contents=[a, b]
        )
        va = resp.embeddings[0].values
        vb = resp.embeddings[1].values
        return max(0.0, min(1.0, float(dot(va, vb))))


def dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


# ---------------------------------------------------------------------------
# Self-healing wrapper
# ---------------------------------------------------------------------------

class DemotingFallback:
    """Wraps the best available API scorer; on the first failure it *permanently*
    demotes to the built-in TF-IDF scorer.

    Ensures that what `provider` reports is always what's actually running: a
    dead/expired API key never silently drops the semantic factor while still
    advertising the API in the header badge.
    """

    def __init__(self, primary, fallback) -> None:
        self._primary = primary
        self._fallback = fallback
        self._active = primary
        self._corpus: list[str] | None = None

    @property
    def provider(self) -> str:
        return self._active.provider

    def fit(self, texts: list[str]) -> None:
        self._corpus = texts
        try:
            self._active.fit(texts)
        except Exception:
            self._demote()

    def similarity(self, a: str, b: str) -> float:
        try:
            return self._active.similarity(a, b)
        except Exception:
            self._demote()
            return self._active.similarity(a, b)

    def _demote(self) -> None:
        if self._active is self._fallback:
            return
        self._active = self._fallback
        if self._corpus:
            self._fallback.fit(self._corpus)


# ---------------------------------------------------------------------------
# Factory / singleton
# ---------------------------------------------------------------------------

_scorer = None


def get_scorer():
    """Build (once) the best available semantic scorer.

    API-based engines are wrapped in a `DemotingFallback` so a bad key visibly
    degrades to TF-IDF instead of silently dropping the semantic factor.
    """
    global _scorer
    if _scorer is not None:
        return _scorer

    if os.getenv("GEMINI_API_KEY"):
        try:
            _scorer = DemotingFallback(GeminiEmbeddingsScorer(), TfidfScorer())
            return _scorer
        except Exception:
            pass  # fall through to the next option

    if os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_BASE_URL"):
        try:
            _scorer = DemotingFallback(OpenAIEmbeddingsScorer(), TfidfScorer())
            return _scorer
        except Exception:
            pass  # fall through to the next option

    if _HAS_SENTENCE_TRANSFORMERS:
        _scorer = SentenceTransformerScorer()
        return _scorer

    _scorer = TfidfScorer()
    return _scorer


def reset_scorer() -> None:
    global _scorer
    _scorer = None


def provider_description() -> tuple[str, str]:
    s = get_scorer()
    return s.provider, explain_provider(s.provider)


def explain_provider(name: str) -> str:
    if name.startswith("gemini"):
        return "Using Google Gemini embeddings for semantic text matching."
    if name.startswith("openai"):
        return "Using an embedding API for semantic text matching."
    if name.startswith("sentence-transformers"):
        return "Using a local neural model installed via pip."
    return "Using the built-in TF-IDF fallback (no dependencies)."