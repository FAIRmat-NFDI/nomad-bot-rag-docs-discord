from typing import Optional
try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None
_model_cache = {}
def _get_model(name: str = "all-MiniLM-L6-v2"):
    if SentenceTransformer is None: return None
    if name not in _model_cache:
        _model_cache[name] = SentenceTransformer(name)
    return _model_cache[name]
def semantic_sim(pred: str, gold: str, model_name: str = "all-MiniLM-L6-v2") -> Optional[float]:
    model = _get_model(model_name)
    if model is None: return None
    emb = model.encode([pred, gold], convert_to_numpy=True, normalize_embeddings=True)
    return float((emb[0] * emb[1]).sum())
