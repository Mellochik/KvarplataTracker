"""rename hws/cws to xvs/gvs

Поле hws на самом деле хранило показания холодной воды (ХВС), а cws — горячей
(ГВС). Чтобы имена не вводили в заблуждение, поля переименовываются:
  * readings.hws_value        -> xvs_value
  * readings.cws_value        -> gvs_value
  * monthly_costs.hws_cost    -> xvs_cost
  * monthly_costs.cws_cost    -> gvs_cost
  * tariffs.resource_type     'hws' -> 'xvs', 'cws' -> 'gvs'

Revision ID: 0002_rename_xvs_gvs
Revises: 0001_remove_note
Create Date: 2026-09-11
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "0002_rename_xvs_gvs"
down_revision = "0001_remove_note"
branch_labels = None
depends_on = None


def _column_names(table: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if table not in inspector.get_table_names():
        return set()
    return {col["name"] for col in inspector.get_columns(table)}


def _rename_column_if_exists(table: str, old: str, new: str) -> None:
    """Переименовать колонку, если она ещё есть (идемпотентность).

    Схема может быть уже переименована приложением или предыдущим прогоном,
    поэтому переименование выполняется только когда старая колонка существует.
    """
    if old in _column_names(table) and new not in _column_names(table):
        with op.batch_alter_table(table) as batch_op:
            batch_op.alter_column(old, new_column_name=new, existing_type=sa.Float())


def upgrade() -> None:
    _rename_column_if_exists("readings", "hws_value", "xvs_value")
    _rename_column_if_exists("readings", "cws_value", "gvs_value")
    _rename_column_if_exists("monthly_costs", "hws_cost", "xvs_cost")
    _rename_column_if_exists("monthly_costs", "cws_cost", "gvs_cost")

    # Значения resource_type в тарифах.
    op.execute("UPDATE tariffs SET resource_type = 'xvs' WHERE resource_type = 'hws'")
    op.execute("UPDATE tariffs SET resource_type = 'gvs' WHERE resource_type = 'cws'")


def downgrade() -> None:
    _rename_column_if_exists("readings", "xvs_value", "hws_value")
    _rename_column_if_exists("readings", "gvs_value", "cws_value")
    _rename_column_if_exists("monthly_costs", "xvs_cost", "hws_cost")
    _rename_column_if_exists("monthly_costs", "gvs_cost", "cws_cost")

    op.execute("UPDATE tariffs SET resource_type = 'hws' WHERE resource_type = 'xvs'")
    op.execute("UPDATE tariffs SET resource_type = 'cws' WHERE resource_type = 'gvs'")
