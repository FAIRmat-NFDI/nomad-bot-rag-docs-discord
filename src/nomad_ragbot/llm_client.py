"""LLM client for generating responses using OpenAI."""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def setup_client():
    """Setup the OpenAI client."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in .env file")
    return OpenAI(api_key=api_key)


def generate_response(prompt, model="gpt-4o-mini", temperature=0.1, max_tokens=1000):
    """Generate response for a given prompt."""
    client = setup_client()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant for NOMAD software.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def generate_rag_response(query, context, model="gpt-4o-mini"):
    """Generate RAG response using retrieved context."""
    system_prompt = """You are a helpful assistant for NOMAD software. Answer the user's question using the provided context from both documentation and community discussions.

If the information comes from community discussions, mention that. If referring to official documentation, indicate that as well. Be concise but thorough."""

    user_prompt = f"""Context:
{context}

Question: {query}

Answer:"""

    client = setup_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,  # Lower for more factual responses
        max_tokens=1000,
    )
    return response.choices[0].message.content
