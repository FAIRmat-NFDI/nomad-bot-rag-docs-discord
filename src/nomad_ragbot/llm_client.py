"""LLM client for generating responses."""

import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

import requests

API_URL = "http://127.0.0.1:8000/ask"


def setup_client():
    """Setup the Gemini client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set in .env file")
    return genai.Client(api_key=api_key)


import re
import requests


def _make_links_clickable(citations_text: str) -> str:
    """
    Convert backtick-wrapped URLs in the citations text into clickable Markdown links.
    """
    if not citations_text:
        return "_No citations provided._"

    # Regex: find backtick-wrapped URLs
    url_pattern = re.compile(r"`(https?://[^\s`]+)`")

    def replacer(match):
        url = match.group(1)
        return f"[{url}]({url})"

    # Replace each backtick-wrapped URL with Markdown link
    clickable = url_pattern.sub(replacer, citations_text)
    return clickable


def generate_response(prompt: str):
    """Call FastAPI /ask and return (answer, citations_markdown)."""
    try:
        resp = requests.post(API_URL, json={"question": prompt}, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        answer = data.get("answer", "")
        citations_raw = data.get("citations", "")
        citations_md = _make_links_clickable(citations_raw)

        return answer, citations_md
    except Exception as e:
        err = f"Error contacting backend: {e}"
        return err, "_No citations due to error._"
