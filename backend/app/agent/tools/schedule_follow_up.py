import uuid
from datetime import date
from typing import Literal

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agent.tools._extraction import extract_structured
from app.api.v1.follow_ups import create_follow_up
from app.models import HCP, Interaction, Rep
from app.schemas.follow_up import FollowUpCreate

_EXTRACTION_PROMPT = (
    "A pharmaceutical sales rep wants to schedule a follow-up reminder. "
    "Today's date is {today}. Read their request below and extract:\n"
    "- hcp_name: the HCP's name, ONLY if mentioned in this request; "
    "leave null if not mentioned.\n"
    "- due_date: the concrete date they want to follow up, resolved "
    "relative to today's date above (e.g. 'next month' means about a "
    "month from today, 'in two weeks' means 14 days from today). Return "
    "an ISO date (YYYY-MM-DD). Leave null if no timeframe is mentioned "
    "at all.\n"
    "- note: a short description of what the follow-up is about.\n\n"
    "Rep's request: {utterance}"
)


class ScheduleFollowUpInput(BaseModel):
    rep_utterance: str
    rep_id: uuid.UUID
    hcp_id: uuid.UUID | None = None
    interaction_id: uuid.UUID | None = None


class HCPCandidate(BaseModel):
    id: uuid.UUID
    name: str
    specialty: str | None = None


class ScheduleFollowUpOutput(BaseModel):
    status: Literal["scheduled", "needs_clarification"]
    message: str
    follow_up_id: uuid.UUID | None = None
    hcp_id: uuid.UUID | None = None
    due_date: date | None = None
    note: str | None = None
    candidate_hcps: list[HCPCandidate] = []


class FollowUpExtraction(BaseModel):
    hcp_name: str | None = None
    due_date: date | None = None
    note: str | None = None


def _extract(rep_utterance: str) -> FollowUpExtraction:
    prompt = _EXTRACTION_PROMPT.format(
        today=date.today().isoformat(), utterance=rep_utterance
    )
    return extract_structured(prompt, FollowUpExtraction)


def _resolve_hcp(
    db: Session, hcp_id: uuid.UUID | None, hcp_name: str | None
) -> HCP | list[HCP] | None:
    if hcp_id is not None:
        hcp = db.get(HCP, hcp_id)
        return hcp if hcp is not None and hcp.is_active else None
    if not hcp_name:
        return None
    stmt = select(HCP).where(HCP.is_active.is_(True), HCP.name.ilike(f"%{hcp_name}%"))
    matches = list(db.scalars(stmt).all())
    if len(matches) == 1:
        return matches[0]
    return matches


def schedule_follow_up(
    payload: ScheduleFollowUpInput, db: Session
) -> ScheduleFollowUpOutput:
    extraction = _extract(payload.rep_utterance)

    resolved = _resolve_hcp(db, payload.hcp_id, extraction.hcp_name)
    if resolved is None or isinstance(resolved, list):
        candidates = resolved or []
        if candidates:
            message = (
                f"I found {len(candidates)} HCPs matching "
                f"'{extraction.hcp_name}' — which one did you mean?"
            )
        else:
            who = extraction.hcp_name or "that HCP"
            message = f"I couldn't find {who} on file — could you confirm the name?"
        return ScheduleFollowUpOutput(
            status="needs_clarification",
            message=message,
            candidate_hcps=[
                HCPCandidate(id=c.id, name=c.name, specialty=c.specialty)
                for c in candidates
            ],
        )
    hcp = resolved

    if extraction.due_date is None:
        return ScheduleFollowUpOutput(
            status="needs_clarification",
            message=(
                "When would you like to follow up? (e.g. 'next month', 'in two weeks')"
            ),
            hcp_id=hcp.id,
        )

    if payload.interaction_id is not None:
        interaction = db.get(Interaction, payload.interaction_id)
        if interaction is None or not interaction.is_active:
            return ScheduleFollowUpOutput(
                status="needs_clarification",
                message="I couldn't find that interaction to attach the follow-up to.",
                hcp_id=hcp.id,
            )

    rep = db.get(Rep, payload.rep_id)
    if rep is None:
        raise ValueError(f"rep_id {payload.rep_id} does not reference an existing rep")

    create_payload = FollowUpCreate(
        hcp_id=hcp.id,
        interaction_id=payload.interaction_id,
        due_date=extraction.due_date,
        note=extraction.note or payload.rep_utterance,
    )
    follow_up = create_follow_up(payload=create_payload, db=db, current_rep=rep)
    due = follow_up.due_date.isoformat()

    return ScheduleFollowUpOutput(
        status="scheduled",
        message=f"Scheduled a follow-up with {hcp.name} for {due}.",
        follow_up_id=follow_up.id,
        hcp_id=hcp.id,
        due_date=follow_up.due_date,
        note=follow_up.note,
    )
