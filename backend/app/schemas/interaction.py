import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

Sentiment = Literal["positive", "neutral", "negative"]
Source = Literal["form", "chat"]
ComplianceFlagCategory = Literal[
    "off_label_claim", "unsubstantiated_claim", "adverse_event_mention", "other"
]


class ComplianceFlag(BaseModel):
    category: ComplianceFlagCategory
    excerpt: str
    rationale: str


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
    compliance_flags: list[ComplianceFlag] | None = None
    has_compliance_flags: bool | None = None


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
    compliance_flags: list[ComplianceFlag]
    has_compliance_flags: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
