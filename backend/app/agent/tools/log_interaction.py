import uuid
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agent.tools._extraction import extract_structured
from app.agent.tools.flag_compliance_risks import (
    FlagComplianceRisksInput,
    flag_compliance_risks,
)
from app.api.v1.interactions import create_interaction, update_interaction
from app.models import HCP, Rep
from app.schemas.interaction import (
    ComplianceFlag,
    InteractionCreate,
    InteractionUpdate,
    Sentiment,
)

_EXTRACTION_PROMPT = (
    "You are helping a pharmaceutical sales rep log a call or meeting with "
    "a healthcare professional (HCP). Extract structured details from the "
    "rep's own description below. Only include what's actually stated or "
    "clearly implied — never invent specifics, and never fill a field with "
    "a placeholder like 'not specified'; leave it null or an empty list "
    "instead.\n\n"
    "Field-specific rules:\n"
    "- attendees: OTHER people present besides the rep and the HCP being "
    "visited (e.g. a nurse, another rep). Do not include the rep or the "
    "HCP themselves. Leave empty if no one else was mentioned.\n"
    "- topics_discussed: a fairly complete account of what was discussed, "
    "in your own words, but preserving every specific claim, statement, or "
    "patient-related comment from the note verbatim or near-verbatim — "
    "do NOT compress this down to just a product name or a one-word "
    "label. This field is also used for downstream compliance review, so "
    "omitting specifics here (e.g. an off-label claim or a mention of a "
    "patient's adverse reaction) means they go unreviewed.\n"
    "- materials_shared: marketing/educational collateral only (brochures, "
    "data sheets, leave-behinds). Never physical product samples.\n"
    "- samples_distributed: physical product samples only (e.g. '2 packs "
    "of CardioX 10mg'). Never marketing materials. The same item must "
    "never appear in both materials_shared and samples_distributed.\n"
    "- outcomes: concrete agreements/results reached during the visit "
    "itself, not future intentions (those belong in suggested_follow_ups).\n"
    "- suggested_follow_ups: 1-3 short, actionable next steps implied by "
    "the note (e.g. a promised follow-up, requested materials).\n\n"
    "Rep's note: {utterance}"
)


class LogInteractionInput(BaseModel):
    rep_utterance: str
    rep_id: uuid.UUID
    hcp_id: uuid.UUID | None = None


class HCPCandidate(BaseModel):
    id: uuid.UUID
    name: str
    specialty: str | None = None


class ExtractedFields(BaseModel):
    hcp_name: str | None = Field(
        default=None, description="Name of the HCP mentioned, if any"
    )
    interaction_type: str | None = Field(
        default=None, description="e.g. Meeting, Call, Email, Conference"
    )
    attendees: list[str] = Field(default_factory=list)
    topics_discussed: str | None = None
    materials_shared: list[str] = Field(default_factory=list)
    samples_distributed: list[str] = Field(default_factory=list)
    sentiment: Sentiment | None = None
    outcomes: str | None = None
    suggested_follow_ups: list[str] = Field(
        default_factory=list,
        description="1-3 short, actionable next-step suggestions",
    )


class LogInteractionOutput(BaseModel):
    status: Literal["created", "needs_clarification"]
    message: str
    interaction_id: uuid.UUID | None = None
    hcp_id: uuid.UUID | None = None
    interaction_type: str | None = None
    occurred_at: datetime | None = None
    attendees: list[str] = []
    topics_discussed: str | None = None
    materials_shared: list[str] = []
    samples_distributed: list[str] = []
    sentiment: Sentiment | None = None
    outcomes: str | None = None
    suggested_follow_ups: list[str] = []
    compliance_flags: list[ComplianceFlag] = []
    candidate_hcps: list[HCPCandidate] = []


def _extract(rep_utterance: str) -> ExtractedFields:
    return extract_structured(
        _EXTRACTION_PROMPT.format(utterance=rep_utterance), ExtractedFields
    )


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


def log_interaction(payload: LogInteractionInput, db: Session) -> LogInteractionOutput:
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
        return LogInteractionOutput(
            status="needs_clarification",
            message=message,
            candidate_hcps=[
                HCPCandidate(id=c.id, name=c.name, specialty=c.specialty)
                for c in candidates
            ],
        )
    hcp = resolved

    if not extraction.topics_discussed and not extraction.outcomes:
        return LogInteractionOutput(
            status="needs_clarification",
            message=(
                "I didn't catch what was discussed — can you give me a bit more detail?"
            ),
            hcp_id=hcp.id,
        )

    rep = db.get(Rep, payload.rep_id)
    if rep is None:
        raise ValueError(f"rep_id {payload.rep_id} does not reference an existing rep")

    create_payload = InteractionCreate(
        hcp_id=hcp.id,
        interaction_type=extraction.interaction_type or "Call",
        occurred_at=datetime.now(UTC),
        attendees=extraction.attendees,
        topics_discussed=extraction.topics_discussed,
        materials_shared=extraction.materials_shared,
        samples_distributed=extraction.samples_distributed,
        sentiment=extraction.sentiment,
        outcomes=extraction.outcomes,
        source="chat",
    )
    interaction = create_interaction(payload=create_payload, db=db, current_rep=rep)
    kind = create_payload.interaction_type.lower()

    screen_text = " ".join(
        part
        for part in (create_payload.topics_discussed, create_payload.outcomes)
        if part
    )
    flags = flag_compliance_risks(FlagComplianceRisksInput(text=screen_text)).flags
    if flags:
        flag_update = InteractionUpdate(
            compliance_flags=flags, has_compliance_flags=True
        )
        interaction = update_interaction(
            interaction_id=interaction.id, payload=flag_update, db=db
        )

    message = f"Logged your {kind} with {hcp.name}."
    if flags:
        categories = ", ".join(sorted({f.category.replace("_", " ") for f in flags}))
        message += (
            f" Heads up — this may involve {categories}; "
            "you may want to review before finalizing."
        )

    return LogInteractionOutput(
        status="created",
        message=message,
        interaction_id=interaction.id,
        hcp_id=hcp.id,
        interaction_type=create_payload.interaction_type,
        occurred_at=create_payload.occurred_at,
        attendees=create_payload.attendees,
        topics_discussed=create_payload.topics_discussed,
        materials_shared=create_payload.materials_shared,
        samples_distributed=create_payload.samples_distributed,
        sentiment=create_payload.sentiment,
        outcomes=create_payload.outcomes,
        suggested_follow_ups=extraction.suggested_follow_ups[:3],
        compliance_flags=flags,
    )
