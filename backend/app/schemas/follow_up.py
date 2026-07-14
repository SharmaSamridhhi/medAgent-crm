import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

FollowUpStatus = Literal["open", "completed", "cancelled"]


class FollowUpCreate(BaseModel):
    hcp_id: uuid.UUID
    interaction_id: uuid.UUID | None = None
    due_date: date
    note: str


class FollowUpRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    interaction_id: uuid.UUID | None
    hcp_id: uuid.UUID
    rep_id: uuid.UUID
    due_date: date
    note: str
    status: FollowUpStatus
    created_at: datetime
