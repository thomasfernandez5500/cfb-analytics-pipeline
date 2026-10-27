"""
Generation half of the RAG layer: takes retrieved context + the model's win
probability and asks a free-tier hosted LLM to write a short, readable blurb.

Supports Groq or Gemini via LLM_PROVIDER in .env. Both have free tiers with
modest daily rate limits -- fine for a portfolio demo, not for production
traffic. Check current limits before you rely on them:
https://groq.com (pricing/docs) or https://ai.google.dev (pricing).
"""
import os
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.environ.get("LLM_PROVIDER", "groq").lower()
API_KEY = os.environ.get("LLM_API_KEY")

PROMPT_TEMPLATE = """You are a concise college football analyst. Given the context
and a model's win probability, write a 2-3 sentence insight for a fan dashboard.
Be specific, avoid hedging filler, and do not invent stats not given to you.

Context:
{context}

Home team win probability: {win_prob:.0%}

Insight:"""


def generate_insight(context: str, win_prob: float) -> str:
    prompt = PROMPT_TEMPLATE.format(context=context, win_prob=win_prob)

    if PROVIDER == "groq":
        return _generate_groq(prompt)
    elif PROVIDER == "gemini":
        return _generate_gemini(prompt)
    else:
        raise ValueError(f"Unknown LLM_PROVIDER '{PROVIDER}'")


def _generate_groq(prompt: str) -> str:
    from groq import Groq
    client = Groq(api_key=API_KEY)
    resp = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
    )
    return resp.choices[0].message.content.strip()


def _generate_gemini(prompt: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-flash-latest")  # TODO: confirm current free model name
    resp = model.generate_content(prompt)
    return resp.text.strip()
