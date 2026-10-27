"""
Builds local embeddings (free, no API calls) over short text blurbs about
each team/game -- recent form, injury notes, whatever context you scrape or
write. This is the "retrieval" half of the RAG insight layer.

TODO: replace DOCS with real content (recent-game recaps, injury reports
pulled from CFBD or elsewhere) once the rest of the pipeline is running.
"""
from sentence_transformers import SentenceTransformer
import numpy as np

MODEL_NAME = "all-MiniLM-L6-v2"  # small, free, runs on CPU

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_documents(docs: list[str]) -> np.ndarray:
    model = _get_model()
    return model.encode(docs, normalize_embeddings=True)


def top_k_relevant(query: str, docs: list[str], k: int = 3) -> list[str]:
    model = _get_model()
    doc_vecs = embed_documents(docs)
    query_vec = model.encode([query], normalize_embeddings=True)[0]
    scores = doc_vecs @ query_vec
    top_idx = np.argsort(-scores)[:k]
    return [docs[i] for i in top_idx]
