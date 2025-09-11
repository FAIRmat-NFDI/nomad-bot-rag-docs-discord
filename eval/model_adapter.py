from typing import Dict, Any


def generate_answer(question: str, meta: Dict[str, Any] | None = None) -> str:
    # TODO: wire into your RAG pipeline, e.g.:
    # from nomad_ragbot.core import <rag_pipeline>
    # return <rag_pipeline>.answer(question, source=meta.get("source") if meta else None)
    return f"[stubbed answer]: {question[:120]}"
