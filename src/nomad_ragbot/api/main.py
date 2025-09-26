# src/api/main.py
from fastapi import FastAPI, HTTPException
import logging

from . import config
from .api_models import QuestionRequest, AnswerResponse, ErrorResponse
from .chroma_logic import ensure_index_up_to_date
from ..query.query import RAGQueryEngine

# --- App Setup ---
app = FastAPI(
    title="MkDocs RAG API",
    description="A server to answer questions about MkDocs documentation using RAG.",
    version="1.0.0"
)

# Use a state object to hold the collection and engine
app.state.collection = None
app.state.rag_engine = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FastAPI Events ---
@app.on_event("startup")
def startup_event():
    """
    On startup, check/build the ChromaDB index and initialize the RAG engine.
    """
    logger.info("Server starting up...")
    try:
        # This function handles all the logic of checking and building the index
        collection = ensure_index_up_to_date()
        app.state.collection = collection
        logger.info("Chroma collection is ready.")

        # Initialize the RAGQueryEngine once the collection is ready
        engine_config = {
            "collection": collection,
            "openai_base_url": config.GENERATOR_BASE_URL,
            "embedding_url": f"{config.EMBED_BASE_URL}/api/embed", # Reconstruct from base
            "embedding_model": config.EMBED_MODEL_NAME,
            "generator_model": config.GENERATOR_MODEL,
            "reranker_model": config.RERANKER_MODEL,
        }
        app.state.rag_engine = RAGQueryEngine(**engine_config)
        logger.info("RAG Query Engine initialized.")

    except Exception as e:
        logger.error(f"FATAL: Failed during startup: {e}", exc_info=True)


# --- API Endpoints ---
@app.post("/ask", response_model=AnswerResponse, responses={500: {"model": ErrorResponse}})
async def ask(req: QuestionRequest):
    """
    Receives a question and returns a generated answer with citations.
    """
    if not app.state.rag_engine:
        raise HTTPException(
            status_code=503,
            detail="The RAG engine is not available. The server may still be starting up."
        )

    try:
        logger.info(f"Received query: '{req.question}'")
        answer, citations, _ = app.state.rag_engine.query(
            req.question,
            top_k=req.top_k,
            rerank_top_n=req.rerank_top_n
        )
        return AnswerResponse(answer=answer, citations=citations)

    except Exception as e:
        logger.error(f"An error occurred while processing the query: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An internal error occurred: {e}"
        )
