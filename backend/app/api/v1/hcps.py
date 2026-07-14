import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import HCP
from app.schemas.hcp import HCPCreate, HCPRead, HCPUpdate

router = APIRouter(prefix="/hcps", tags=["hcps"])


def _get_active_hcp(db: Session, hcp_id: uuid.UUID) -> HCP:
    hcp = db.get(HCP, hcp_id)
    if hcp is None or not hcp.is_active:
        raise HTTPException(status_code=404, detail="HCP not found")
    return hcp


@router.get("", response_model=list[HCPRead])
def list_hcps(
    search: str | None = Query(default=None, description="ILIKE match on name"),
    specialty: str | None = Query(default=None, description="ILIKE match on specialty"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[HCP]:
    stmt = select(HCP).where(HCP.is_active.is_(True))
    if search:
        stmt = stmt.where(HCP.name.ilike(f"%{search}%"))
    if specialty:
        stmt = stmt.where(HCP.specialty.ilike(f"%{specialty}%"))
    stmt = stmt.order_by(HCP.name).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


@router.get("/{hcp_id}", response_model=HCPRead)
def get_hcp(hcp_id: uuid.UUID, db: Session = Depends(get_db)) -> HCP:
    return _get_active_hcp(db, hcp_id)


@router.post("", response_model=HCPRead, status_code=201)
def create_hcp(payload: HCPCreate, db: Session = Depends(get_db)) -> HCP:
    hcp = HCP(**payload.model_dump())
    db.add(hcp)
    db.commit()
    db.refresh(hcp)
    return hcp


@router.patch("/{hcp_id}", response_model=HCPRead)
def update_hcp(
    hcp_id: uuid.UUID, payload: HCPUpdate, db: Session = Depends(get_db)
) -> HCP:
    hcp = _get_active_hcp(db, hcp_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(hcp, field, value)
    db.commit()
    db.refresh(hcp)
    return hcp


@router.delete("/{hcp_id}", status_code=204)
def delete_hcp(hcp_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    hcp = _get_active_hcp(db, hcp_id)
    hcp.is_active = False
    db.commit()
