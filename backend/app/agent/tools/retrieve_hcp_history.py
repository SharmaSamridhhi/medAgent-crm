import uuid
from datetime import datetime
from typing import Literal, cast

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agent.llm import get_default_llm
from app.api.v1.hcps import get_hcp, list_hcps
from app.api.v1.interactions import list_interactions
from app.models import HCP, Interaction
from app.schemas.interaction import Sentiment

_HISTORY_LIMIT = 10

_SUMMARY_PROMPT = (
    "Summarize this pharma sales rep's relationship with an HCP in 1-2 "
    "short sentences, based on their past interactions below. Mention "
    "roughly how many interactions, the main topics, and anything "
    "forward-looking (a promised follow-up, outstanding request). Be "
    "concise — this is a quick briefing, not a report.\n\n"
    "HCP: {hcp_name}\n\n"
    "Past interactions (most recent first):\n{interactions}"
)


class RetrieveHCPHistoryInput(BaseModel):
    hcp_id: uuid.UUID | None = None
    hcp_name: str | None = None


class HCPCandidate(BaseModel):
    id: uuid.UUID
    name: str
    specialty: str | None = None


class InteractionSummary(BaseModel):
    id: uuid.UUID
    occurred_at: datetime
    interaction_type: str
    topics_discussed: str | None
    sentiment: Sentiment | None
    outcomes: str | None


class RetrieveHCPHistoryOutput(BaseModel):
    status: Literal["found", "needs_clarification"]
    message: str
    hcp_id: uuid.UUID | None = None
    hcp_name: str | None = None
    specialty: str | None = None
    institution: str | None = None
    interactions: list[InteractionSummary] = []
    summary: str | None = None
    candidate_hcps: list[HCPCandidate] = []


def _get_hcp_by_id(db: Session, hcp_id: uuid.UUID) -> HCP | None:
    try:
        return get_hcp(hcp_id, db=db)
    except HTTPException:
        return None


def _search_hcps_by_name(db: Session, hcp_name: str) -> list[HCP]:
    return list_hcps(search=hcp_name, specialty=None, skip=0, limit=20, db=db)


def _resolve_hcp(
    db: Session, hcp_id: uuid.UUID | None, hcp_name: str | None
) -> HCP | list[HCP] | None:
    if hcp_id is not None:
        return _get_hcp_by_id(db, hcp_id)
    if not hcp_name:
        return None
    matches = _search_hcps_by_name(db, hcp_name)
    if len(matches) == 1:
        return matches[0]
    return matches


def _format_interactions(interactions: list[Interaction]) -> str:
    lines = [
        f"- {i.occurred_at.date()} ({i.interaction_type}): "
        f"{i.topics_discussed or 'no topic recorded'}; "
        f"sentiment={i.sentiment or 'unknown'}; "
        f"outcomes={i.outcomes or 'none recorded'}"
        for i in interactions
    ]
    return "\n".join(lines)


def _summarize(hcp_name: str, interactions: list[Interaction]) -> str:
    if not interactions:
        return "No prior interactions on file yet."
    prompt = _SUMMARY_PROMPT.format(
        hcp_name=hcp_name, interactions=_format_interactions(interactions)
    )
    response = get_default_llm().invoke(prompt)
    return str(response.content)


def retrieve_hcp_history(
    payload: RetrieveHCPHistoryInput, db: Session
) -> RetrieveHCPHistoryOutput:
    resolved = _resolve_hcp(db, payload.hcp_id, payload.hcp_name)
    if resolved is None or isinstance(resolved, list):
        candidates = resolved or []
        if not candidates:
            who = payload.hcp_name or "that HCP"
            message = f"I couldn't find {who} on file — could you confirm the name?"
        else:
            message = (
                f"I found {len(candidates)} HCPs matching "
                f"'{payload.hcp_name}' — which one did you mean?"
            )
        return RetrieveHCPHistoryOutput(
            status="needs_clarification",
            message=message,
            candidate_hcps=[
                HCPCandidate(id=c.id, name=c.name, specialty=c.specialty)
                for c in candidates
            ],
        )
    hcp = resolved

    interactions = list_interactions(
        hcp_id=hcp.id,
        rep_id=None,
        occurred_from=None,
        occurred_to=None,
        skip=0,
        limit=_HISTORY_LIMIT,
        db=db,
    )

    summary = _summarize(hcp.name, interactions)

    return RetrieveHCPHistoryOutput(
        status="found",
        message=f"Found {len(interactions)} recent interaction(s) with {hcp.name}.",
        hcp_id=hcp.id,
        hcp_name=hcp.name,
        specialty=hcp.specialty,
        institution=hcp.institution,
        interactions=[
            InteractionSummary(
                id=i.id,
                occurred_at=i.occurred_at,
                interaction_type=i.interaction_type,
                topics_discussed=i.topics_discussed,
                sentiment=cast("Sentiment | None", i.sentiment),
                outcomes=i.outcomes,
            )
            for i in interactions
        ],
        summary=summary,
    )
