"""remove note columns

Заметки больше не используются, поэтому колонка note удаляется из таблиц
readings и monthly_costs.

Revision ID: 0001_remove_note
Revises:
Create Date: 2026-09-10
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "0001_remove_note"
down_revision = None
branch_labels = None
depends_on = None


def _table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _column_names(table: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if table not in inspector.get_table_names():
        return set()
    return {col["name"] for col in inspector.get_columns(table)}


def upgrade() -> None:
    # Колонка удаляется только если реально существует: схема создаётся
    # приложением (create_all), поэтому состояние таблиц может отличаться.
    for table in ("readings", "monthly_costs"):
        if "note" in _column_names(table):
            with op.batch_alter_table(table) as batch_op:
                batch_op.drop_column("note")


def downgrade() -> None:
    # В исходной схеме поле note было только в monthly_costs.
    if "monthly_costs" in _table_names() and "note" not in _column_names("monthly_costs"):
        with op.batch_alter_table("monthly_costs") as batch_op:
            batch_op.add_column(sa.Column("note", sa.String(length=100), nullable=True))
