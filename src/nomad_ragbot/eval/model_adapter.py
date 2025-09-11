# nomad_ragbot/eval/model_adapter.py
from typing import Dict, Any
import os, requests

# Configure via env if needed
API_BASE = os.getenv("NOMAD_RAGBOT_API_URL", "http://127.0.0.1:8000")
ASK_PATH = os.getenv("NOMAD_RAGBOT_ASK_PATH", "/ask")
TIMEOUT_S = float(os.getenv("NOMAD_RAGBOT_TIMEOUT", "30"))

_session = requests.Session()


def _ask_api(question: str) -> str:
    """Call the FastAPI RAG endpoint and return the model's text response."""
    url = f"{API_BASE.rstrip('/')}{ASK_PATH}"
    resp = _session.post(url, json={"question": question}, timeout=TIMEOUT_S)
    resp.raise_for_status()
    data = resp.json()
    # Your server returns {"response": "..."} on success
    if isinstance(data, dict) and "response" in data and data["response"]:
        return str(data["response"]).strip()
    # Fallbacks
    if isinstance(data, dict) and "error" in data:
        return f"[model error] {data['error']}"
    return f"[model error] Unexpected response payload: {data}"


def generate_answer(question: str, meta: Dict[str, Any] | None = None) -> str:
    """
    Adapter used by the eval pipeline. Returns plain text for scoring.
    Note: your FastAPI server keeps a global chat_history; for deterministic
    evals you may want to make the endpoint stateless or add a `/reset` call.
    """
    try:
        return _ask_api(question)
    except Exception as e:
        return f"[model error] {e.__class__.__name__}: {e}"
