import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.dependencies import get_current_rep
from app.models import HCP, Interaction, Rep
from app.schemas.interaction import (
    InteractionCreate,
    InteractionRead,
    InteractionUpdate,
)

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
