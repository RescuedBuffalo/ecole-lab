"""math tables"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002_math"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "participants",
        sa.Column("participant_id", sa.String(), primary_key=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column("age_band", sa.String(), nullable=True),
        sa.Column("interests", sa.JSON(), nullable=True),
    )
    op.create_table(
        "sessions",
        sa.Column("session_id", sa.String(), primary_key=True),
        sa.Column(
            "participant_id", sa.String(), sa.ForeignKey("participants.participant_id")
        ),
        sa.Column("skill", sa.String(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("post_quiz", sa.JSON(), nullable=True),
    )
    op.create_table(
        "items",
        sa.Column("item_id", sa.String(), primary_key=True),
        sa.Column("session_id", sa.String(), sa.ForeignKey("sessions.session_id")),
        sa.Column("problem_spec", sa.JSON(), nullable=False),
        sa.Column("context_id", sa.String(), nullable=False),
        sa.Column("variant", sa.String(), nullable=False),
        sa.Column("motif", sa.String(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )
    op.create_table(
        "attempts",
        sa.Column("attempt_id", sa.String(), primary_key=True),
        sa.Column("item_id", sa.String(), sa.ForeignKey("items.item_id")),
        sa.Column("shown_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("answer_submitted", sa.Float(), nullable=True),
        sa.Column("first_try_correct", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("time_to_first_try_ms", sa.Integer(), nullable=True),
        sa.Column("hints_used", sa.Integer(), server_default="0"),
        sa.Column("retries", sa.Integer(), server_default="0"),
    )


def downgrade() -> None:
    op.drop_table("attempts")
    op.drop_table("items")
    op.drop_table("sessions")
    op.drop_table("participants")
