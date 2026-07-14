import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HCPCreate(BaseModel):
    name: str
    specialty: str | None = None
    institution: str | None = None
    contact_info: str | None = None


class HCPUpdate(BaseModel):
    name: str | None = None
    specialty: str | None = None
    institution: str | None = None
    contact_info: str | None = None


class HCPRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    specialty: str | None
    institution: str | None
    contact_info: str | None
    is_active: bool
    created_at: datetime
