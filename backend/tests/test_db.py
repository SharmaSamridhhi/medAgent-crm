from sqlalchemy import select

from app.core.db import SessionLocal
from app.models import Rep


def test_can_connect_and_query_empty_table() -> None:
    with SessionLocal() as session:
        reps = session.scalars(select(Rep)).all()
        assert reps == []
