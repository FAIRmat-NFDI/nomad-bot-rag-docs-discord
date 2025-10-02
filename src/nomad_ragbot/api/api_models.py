# src/api/api_models.py
from pydantic import BaseModel
from typing import Optional

class QuestionRequest(BaseModel):
    question: str
    top_k: Optional[int] = 5
    rerank_top_n: Optional[int] = 20

class AnswerResponse(BaseModel):
    answer: str
    citations: str

class ErrorResponse(BaseModel):
    error: str
