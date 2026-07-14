import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.dependencies import get_current_rep
from app.models import HCP, FollowUp, Interaction, Rep
from app.schemas.follow_up import FollowUpCreate, FollowUpRead, FollowUpStatus

router = APIRouter(prefix="/follow-ups", tags=["follow-ups"])


def _require_active_hcp(db: Session, hcp_id: uuid.UUID) -> None:
    hcp = db.get(HCP, hcp_id)
    if hcp is None or not hcp.is_active:
        raise HTTPException(
            status_code=422, detail=f"hcp_id {hcp_id} does not reference an active HCP"
        )


def _require_active_interaction(db: Session, interaction_id: uuid.UUID) -> None:
    interaction = db.get(Interaction, interaction_id)
    if interaction is None or not interaction.is_active:
        raise HTTPException(
            status_code=422,
            detail=(
                f"interaction_id {interaction_id} does not reference "
                "an active interaction"
            ),
        )


@router.get("", response_model=list[FollowUpRead])
def list_follow_ups(
    status: FollowUpStatus | None = Query(default=None),
    db: Session = Depends(get_db),
    current_rep: Rep = Depends(get_current_rep),
) -> list[FollowUp]:
    stmt = select(FollowUp).where(FollowUp.rep_id == current_rep.id)
    if status is not None:
        stmt = stmt.where(FollowUp.status == status)
    stmt = stmt.order_by(FollowUp.due_date.asc())
    return list(db.scalars(stmt).all())


@router.post("", response_model=FollowUpRead, status_code=201)
def create_follow_up(
    payload: FollowUpCreate,
    db: Session = Depends(get_db),
    current_rep: Rep = Depends(get_current_rep),
) -> FollowUp:
    _require_active_hcp(db, payload.hcp_id)
    if payload.interaction_id is not None:
        _require_active_interaction(db, payload.interaction_id)
    follow_up = FollowUp(**payload.model_dump(), rep_id=current_rep.id)
    db.add(follow_up)
    db.commit()
    db.refresh(follow_up)
    return follow_up


@router.post("/{follow_up_id}/complete", response_model=FollowUpRead)
def complete_follow_up(
    follow_up_id: uuid.UUID, db: Session = Depends(get_db)
) -> FollowUp:
    follow_up = db.get(FollowUp, follow_up_id)
    if follow_up is None:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    follow_up.status = "completed"
    db.commit()
    db.refresh(follow_up)
    return follow_up
