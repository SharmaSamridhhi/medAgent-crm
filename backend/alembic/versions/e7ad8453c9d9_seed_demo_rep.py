"""seed demo rep

Revision ID: e7ad8453c9d9
Revises: dd918c1a0d80
Create Date: 2026-07-14 14:51:24.684672

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e7ad8453c9d9"
down_revision: str | Sequence[str] | None = "dd918c1a0d80"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Matches app.core.config.DEFAULT_DEMO_REP_ID — this build has no auth
# system, so get_current_rep resolves to this one seeded row.
DEMO_REP_ID = "00000000-0000-0000-0000-000000000001"


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        sa.text(
            "INSERT INTO reps (id, name, email) "
            "VALUES (CAST(:id AS UUID), :name, :email) "
            "ON CONFLICT (id) DO NOTHING"
        ).bindparams(
            id=DEMO_REP_ID, name="Demo Rep", email="demo.rep@medagent-crm.local"
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        sa.text("DELETE FROM reps WHERE id = CAST(:id AS UUID)").bindparams(
            id=DEMO_REP_ID
        )
    )
