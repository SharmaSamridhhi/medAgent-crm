from sqlalchemy import select

from app.core.db import SessionLocal
from app.models import HCP


def test_can_connect_and_query() -> None:
    with SessionLocal() as session:
        hcps = session.scalars(select(HCP)).all()
        assert isinstance(hcps, list)
