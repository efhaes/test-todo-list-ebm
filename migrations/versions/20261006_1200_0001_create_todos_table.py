"""create todos table

Revision ID: 0001
Revises:
Create Date: 2026-10-06 12:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# Identitas migration ini. down_revision=None artinya ini migration PERTAMA.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Dijalankan oleh `alembic upgrade head`: membuat tabel todos + index."""
    op.create_table(
        "todos",
        sa.Column("id", sa.CHAR(36), nullable=False),  # UUID v7 sebagai teks 36 karakter
        sa.Column("title", sa.String(length=255), nullable=False),
        # ENUM native MySQL: database menolak nilai di luar daftar
        sa.Column(
            "status",
            sa.Enum("pending", "progress", "done", name="todo_status"),
            nullable=False,
        ),
        sa.Column(
            "priority",
            sa.Enum("low", "medium", "high", name="todo_priority"),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=True),
        # DATETIME(6) = presisi mikrodetik (supaya sorting waktu akurat)
        sa.Column(
            "created_at",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",  # mendukung emoji & karakter non-latin
    )
    # Index untuk kolom yang sering dipakai filter / sorting / search
    op.create_index(op.f("ix_todos_title"), "todos", ["title"])
    op.create_index(op.f("ix_todos_status"), "todos", ["status"])
    op.create_index(op.f("ix_todos_priority"), "todos", ["priority"])
    op.create_index(op.f("ix_todos_created_at"), "todos", ["created_at"])


def downgrade() -> None:
    """Dijalankan oleh `alembic downgrade -1`: membatalkan upgrade di atas."""
    op.drop_index(op.f("ix_todos_created_at"), table_name="todos")
    op.drop_index(op.f("ix_todos_priority"), table_name="todos")
    op.drop_index(op.f("ix_todos_status"), table_name="todos")
    op.drop_index(op.f("ix_todos_title"), table_name="todos")
    op.drop_table("todos")