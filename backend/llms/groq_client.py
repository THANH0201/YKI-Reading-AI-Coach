# backend/llms/groq_client.py

from langchain_groq import ChatGroq

from backend.config.settings import settings


def get_groq_llm():

    return ChatGroq(
        model=settings.GROQ_MODEL,
        temperature=0.3,
        timeout=15,
        max_retries=0,
    )
