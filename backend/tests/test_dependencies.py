from app.core.config import get_settings
from app.core.db import SessionLocal
from app.core.dependencies import get_current_rep


def test_get_current_rep_resolves_seeded_demo_rep() -> None:
    with SessionLocal() as db:
        rep = get_current_rep(db=db)

    assert rep.id == get_settings().default_rep_id
    assert rep.name == "Demo Rep"
