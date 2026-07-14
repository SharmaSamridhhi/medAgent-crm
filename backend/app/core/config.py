import uuid
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# Fixed id of the single demo rep seeded by the Alembic migration in this
# spec. No auth system in this build — see steering/04-architecture-tech-stack.md.
DEFAULT_DEMO_REP_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    default_rep_id: uuid.UUID = DEFAULT_DEMO_REP_ID
    cors_origins: str = "http://localhost:5173"

    # Not consumed until MEDGENT-009 wires up the Groq client, but the
    # settings surface is established here per this spec's scope.
    groq_api_key: str | None = None
    groq_model_default: str = "gemma2-9b-it"
    groq_model_heavy: str = "llama-3.3-70b-versatile"

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
