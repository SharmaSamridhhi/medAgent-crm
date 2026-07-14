from langchain_groq import ChatGroq
from pydantic import SecretStr

from app.core.config import get_settings


def _api_key() -> SecretStr | None:
    key = get_settings().groq_api_key
    return SecretStr(key) if key else None


def get_default_llm() -> ChatGroq:
    """Fast model for conversational turns (see steering/04)."""
    settings = get_settings()
    return ChatGroq(model=settings.groq_model_default, api_key=_api_key())


def get_heavy_llm() -> ChatGroq:
    """Heavier model for structured extraction / compliance review steps."""
    settings = get_settings()
    return ChatGroq(model=settings.groq_model_heavy, api_key=_api_key())
