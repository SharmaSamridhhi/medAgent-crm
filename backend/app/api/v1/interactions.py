import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agent.tools.flag_compliance_risks import (
    FlagComplianceRisksInput,
    flag_compliance_risks,
)
from app.core.db import get_db
from app.core.dependencies import get_current_rep
from app.models import HCP, Interaction, Rep
from app.schemas.interaction import (
    InteractionCreate,
    InteractionRead,
    InteractionUpdate,
)

# Fields whose edit can introduce a new compliance risk (off-label claims,
# unsubstantiated claims, adverse-event mentions) — see MEDGENT-022.
_COMPLIANCE_SCREENED_FIELDS = ("topics_discussed", "outcomes")

router = APIRouter(prefix="/interactions", tags=["interactions"])


def _get_active_interaction(db: Session, interaction_id: uuid.UUID) -> Interaction:
    interaction = db.get(Interaction, interaction_id)
    if interaction is None or not interaction.is_active:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction


def _require_active_hcp(db: Session, hcp_id: uuid.UUID) -> None:
    hcp = db.get(HCP, hcp_id)
    if hcp is None or not hcp.is_active:
        raise HTTPException(
            status_code=422, detail=f"hcp_id {hcp_id} does not reference an active HCP"
        )


@router.get("", response_model=list[InteractionRead])
def list_interactions(
    hcp_id: uuid.UUID | None = Query(default=None),
    rep_id: uuid.UUID | None = Query(default=None),
    occurred_from: datetime | None = Query(default=None),
    occurred_to: datetime | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[Interaction]:
    stmt = select(Interaction).where(Interaction.is_active.is_(True))
    if hcp_id is not None:
        stmt = stmt.where(Interaction.hcp_id == hcp_id)
    if rep_id is not None:
        stmt = stmt.where(Interaction.rep_id == rep_id)
    if occurred_from is not None:
        stmt = stmt.where(Interaction.occurred_at >= occurred_from)
    if occurred_to is not None:
        stmt = stmt.where(Interaction.occurred_at <= occurred_to)
    stmt = stmt.order_by(Interaction.occurred_at.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


@router.get("/{interaction_id}", response_model=InteractionRead)
def get_interaction(
    interaction_id: uuid.UUID, db: Session = Depends(get_db)
) -> Interaction:
    return _get_active_interaction(db, interaction_id)


@router.post("", response_model=InteractionRead, status_code=201)
def create_interaction(
    payload: InteractionCreate,
    db: Session = Depends(get_db),
    current_rep: Rep = Depends(get_current_rep),
) -> Interaction:
    _require_active_hcp(db, payload.hcp_id)
    interaction = Interaction(**payload.model_dump(), rep_id=current_rep.id)
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


@router.patch("/{interaction_id}", response_model=InteractionRead)
def update_interaction(
    interaction_id: uuid.UUID,
    payload: InteractionUpdate,
    db: Session = Depends(get_db),
) -> Interaction:
    interaction = _get_active_interaction(db, interaction_id)
    updates = payload.model_dump(exclude_unset=True)
    if "hcp_id" in updates:
        _require_active_hcp(db, updates["hcp_id"])
    for field, value in updates.items():
        setattr(interaction, field, value)

    # Editing the notes can introduce a new compliance risk that wasn't
    # present (or wasn't screened) at creation time — re-screen unless the
    # caller is explicitly setting compliance_flags itself in this same
    # request (e.g. log_interaction's own post-create flagging call).
    if (
        any(field in updates for field in _COMPLIANCE_SCREENED_FIELDS)
        and "compliance_flags" not in updates
    ):
        screen_text = " ".join(
            part
            for part in (interaction.topics_discussed, interaction.outcomes)
            if part
        )
        flags = flag_compliance_risks(FlagComplianceRisksInput(text=screen_text)).flags
        interaction.compliance_flags = [flag.model_dump(mode="json") for flag in flags]
        interaction.has_compliance_flags = bool(flags)

    db.commit()
    db.refresh(interaction)
    return interaction


@router.delete("/{interaction_id}", status_code=204)
def delete_interaction(
    interaction_id: uuid.UUID, db: Session = Depends(get_db)
) -> None:
    interaction = _get_active_interaction(db, interaction_id)
    interaction.is_active = False
    db.commit()
