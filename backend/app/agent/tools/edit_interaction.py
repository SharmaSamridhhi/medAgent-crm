import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agent.tools._extraction import extract_structured
from app.api.v1.interactions import update_interaction
from app.models import HCP, Interaction
from app.schemas.interaction import InteractionUpdate, Sentiment

_RECENT_WINDOW = timedelta(days=7)

_EDITABLE_FIELDS = (
    "interaction_type",
    "attendees",
    "topics_discussed",
    "materials_shared",
    "samples_distributed",
    "sentiment",
    "outcomes",
    "follow_up_notes",
)

_HINT_PROMPT = (
    "A pharmaceutical sales rep is correcting an interaction they logged "
    "earlier, but it's ambiguous which one. If they name the HCP in this "
    "message, extract the name; otherwise leave it null.\n\n"
    "Rep's correction: {utterance}"
)

_DIFF_PROMPT = (
    "A pharmaceutical sales rep is correcting or adding to an interaction "
    "they already logged with a healthcare professional (HCP). Here is "
    "the interaction's CURRENT recorded data:\n"
    "{current_state}\n\n"
    "Read the rep's correction below and work out the NEW value for any "
    "field they are explicitly changing, in light of the current data "
    "above — e.g. 'it was 3, not 2' about samples means samples_distributed "
    "should become the current list with that quantity corrected, not a "
    "made-up replacement. Leave every field the rep did NOT address as "
    "null/empty; do not restate unrelated current values.\n\n"
    "For list fields (attendees, materials_shared, samples_distributed): "
    "if anything in that list changes, return the FULL corrected list "
    "(informed by the current data above), not just the changed item.\n\n"
    "Rep's correction: {utterance}"
)


class EditInteractionInput(BaseModel):
    rep_utterance: str
    rep_id: uuid.UUID
    interaction_id: uuid.UUID | None = None


class InteractionCandidate(BaseModel):
    id: uuid.UUID
    hcp_name: str
    occurred_at: datetime


class FieldChange(BaseModel):
    field: str
    old_value: Any
    new_value: Any


class EditInteractionOutput(BaseModel):
    status: Literal["updated", "needs_clarification"]
    message: str
    interaction_id: uuid.UUID | None = None
    changes: list[FieldChange] = []
    candidate_interactions: list[InteractionCandidate] = []


class HCPNameHint(BaseModel):
    target_hcp_name: str | None = None


class EditExtraction(BaseModel):
    interaction_type: str | None = None
    attendees: list[str] | None = None
    topics_discussed: str | None = None
    materials_shared: list[str] | None = None
    samples_distributed: list[str] | None = None
    sentiment: Sentiment | None = None
    outcomes: str | None = None
    follow_up_notes: str | None = None


def _recent_candidates(db: Session, rep_id: uuid.UUID) -> list[Interaction]:
    cutoff = datetime.now(UTC) - _RECENT_WINDOW
    stmt = (
        select(Interaction)
        .where(
            Interaction.rep_id == rep_id,
            Interaction.is_active.is_(True),
            Interaction.created_at >= cutoff,
        )
        .order_by(Interaction.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def _filter_by_hcp_name(
    db: Session, candidates: list[Interaction], hcp_name: str
) -> list[Interaction]:
    matches = []
    for candidate in candidates:
        hcp = db.get(HCP, candidate.hcp_id)
        if hcp is not None and hcp_name.lower() in hcp.name.lower():
            matches.append(candidate)
    return matches


def _resolve_interaction(
    db: Session,
    rep_id: uuid.UUID,
    interaction_id: uuid.UUID | None,
    rep_utterance: str,
) -> Interaction | list[Interaction] | None:
    if interaction_id is not None:
        interaction = db.get(Interaction, interaction_id)
        if interaction is not None and interaction.is_active:
            return interaction
        return None

    candidates = _recent_candidates(db, rep_id)
    if len(candidates) <= 1:
        return candidates[0] if candidates else []

    hint = extract_structured(_HINT_PROMPT.format(utterance=rep_utterance), HCPNameHint)
    if hint.target_hcp_name:
        filtered = _filter_by_hcp_name(db, candidates, hint.target_hcp_name)
        if len(filtered) == 1:
            return filtered[0]
        return filtered or candidates
    return candidates


def _candidate_summaries(
    db: Session, candidates: list[Interaction]
) -> list[InteractionCandidate]:
    summaries = []
    for interaction in candidates:
        hcp = db.get(HCP, interaction.hcp_id)
        summaries.append(
            InteractionCandidate(
                id=interaction.id,
                hcp_name=hcp.name if hcp is not None else "Unknown HCP",
                occurred_at=interaction.occurred_at,
            )
        )
    return summaries


def _format_current_state(interaction: Interaction) -> str:
    return (
        f"- interaction_type: {interaction.interaction_type}\n"
        f"- attendees: {interaction.attendees}\n"
        f"- topics_discussed: {interaction.topics_discussed}\n"
        f"- materials_shared: {interaction.materials_shared}\n"
        f"- samples_distributed: {interaction.samples_distributed}\n"
        f"- sentiment: {interaction.sentiment}\n"
        f"- outcomes: {interaction.outcomes}\n"
        f"- follow_up_notes: {interaction.follow_up_notes}"
    )


def _extract_diff(rep_utterance: str, interaction: Interaction) -> EditExtraction:
    prompt = _DIFF_PROMPT.format(
        current_state=_format_current_state(interaction), utterance=rep_utterance
    )
    return extract_structured(prompt, EditExtraction)


def edit_interaction(
    payload: EditInteractionInput, db: Session
) -> EditInteractionOutput:
    resolved = _resolve_interaction(
        db, payload.rep_id, payload.interaction_id, payload.rep_utterance
    )
    if resolved is None or isinstance(resolved, list):
        candidates = resolved or []
        if not candidates:
            message = (
                "I don't see a recent interaction to edit — "
                "could you tell me which one?"
            )
        else:
            message = (
                f"I found {len(candidates)} recent interactions — "
                "which one did you mean, or which HCP was it with?"
            )
        return EditInteractionOutput(
            status="needs_clarification",
            message=message,
            candidate_interactions=_candidate_summaries(db, candidates),
        )
    interaction = resolved

    extraction = _extract_diff(payload.rep_utterance, interaction)

    changes: list[FieldChange] = []
    updates: dict[str, Any] = {}
    for field in _EDITABLE_FIELDS:
        new_value = getattr(extraction, field)
        if new_value is None:
            continue
        old_value = getattr(interaction, field)
        if new_value != old_value:
            updates[field] = new_value
            changes.append(
                FieldChange(field=field, old_value=old_value, new_value=new_value)
            )

    if not updates:
        return EditInteractionOutput(
            status="needs_clarification",
            message=(
                "I couldn't tell what you'd like to change — "
                "could you be more specific?"
            ),
            interaction_id=interaction.id,
        )

    updated = update_interaction(
        interaction_id=interaction.id, payload=InteractionUpdate(**updates), db=db
    )

    hcp = db.get(HCP, updated.hcp_id)
    hcp_name = hcp.name if hcp is not None else "the HCP"
    return EditInteractionOutput(
        status="updated",
        message=f"Updated {len(changes)} field(s) on the interaction with {hcp_name}.",
        interaction_id=updated.id,
        changes=changes,
    )
