from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.models import Rep


def get_current_rep(db: Session = Depends(get_db)) -> Rep:
    settings = get_settings()
    rep = db.get(Rep, settings.default_rep_id)
    if rep is None:
        raise HTTPException(
            status_code=500,
            detail=(
                "Demo rep not seeded — run migrations "
                "(alembic upgrade head) before serving requests."
            ),
        )
    return rep
