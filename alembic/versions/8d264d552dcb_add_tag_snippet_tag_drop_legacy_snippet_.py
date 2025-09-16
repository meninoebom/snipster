"""add tag & snippet_tag; drop legacy snippet.tags

Revision ID: 8d264d552dcb
Revises: 9294fad3ea8f
Create Date: 2025-09-11 18:44:29.916899
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "8d264d552dcb"
down_revision: Union[str, Sequence[str], None] = "9294fad3ea8f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # tag table
    op.create_table(
        "tag",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=50), nullable=False),
    )
    op.create_index(op.f("ix_tag_name"), "tag", ["name"], unique=False)
    op.create_index("uq_tag_name_lower", "tag", [sa.text("lower(name)")], unique=True)

    # association table with DB cascades
    op.create_table(
        "snippet_tag",
        sa.Column("snippet_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["snippet_id"], ["snippet.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tag.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("snippet_id", "tag_id", name="pk_snippet_tag"),
    )
    op.create_index("ix_snippet_tag_snippet_id", "snippet_tag", ["snippet_id"])
    op.create_index("ix_snippet_tag_tag_id", "snippet_tag", ["tag_id"])

    # drop legacy JSON column (SQLite-safe)
    with op.batch_alter_table("snippet") as b:
        b.drop_column("tags")


def downgrade() -> None:
    with op.batch_alter_table("snippet") as b:
        b.add_column(sa.Column("tags", sa.JSON(), nullable=True))

    op.drop_index("ix_snippet_tag_tag_id", table_name="snippet_tag")
    op.drop_index("ix_snippet_tag_snippet_id", table_name="snippet_tag")
    op.drop_table("snippet_tag")

    op.drop_index("uq_tag_name_lower", table_name="tag")
    op.drop_index(op.f("ix_tag_name"), table_name="tag")
    op.drop_table("tag")
