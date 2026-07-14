import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

Sentiment = Literal["positive", "neutral", "negative"]
Source = Literal["form", "chat"]


class InteractionCreate(BaseModel):
    hcp_id: uuid.UUID
    interaction_type: str
    occurred_at: datetime
    attendees: list[str] = []
    topics_discussed: str | None = None
    materials_shared: list[str] = []
    samples_distributed: list[str] = []
    sentiment: Sentiment | None = None
    outcomes: str | None = None
    follow_up_notes: str | None = None
    source: Source = "form"


class InteractionUpdate(BaseModel):
    hcp_id: uuid.UUID | None = None
    interaction_type: str | None = None
    occurred_at: datetime | None = None
    attendees: list[str] | None = None
    topics_discussed: str | None = None
    materials_shared: list[str] | None = None
    samples_distributed: list[str] | None = None
    sentiment: Sentiment | None = None
    outcomes: str | None = None
    follow_up_notes: str | None = None
    source: Source | None = None


class InteractionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    hcp_id: uuid.UUID
    rep_id: uuid.UUID
    interaction_type: str
    occurred_at: datetime
    attendees: list[str]
    topics_discussed: str | None
    materials_shared: list[str]
    samples_distributed: list[str]
    sentiment: Sentiment | None
    outcomes: str | None
    follow_up_notes: str | None
    source: Source
    is_active: bool
    created_at: datetime
    updated_at: datetime
