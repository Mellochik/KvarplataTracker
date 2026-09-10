from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import MonthlyCost, Reading, Tariff
from app.schemas import MonthlyCostRead, StatsRead, YearSummary
from app.services.calculator import TariffSet, calculate_month

router = APIRouter(prefix="/api/summary", tags=["summary"])


def _rate_for(tariffs: list[Tariff], resource_type: str, period: date) -> float:
    """Resolve the tariff rate effective for the given month."""
    candidates = [
        t
        for t in tariffs
        if t.resource_type == resource_type
        and t.effective_from <= period
        and (t.effective_to is None or t.effective_to >= period)
    ]
    if not candidates:
        return 0.0
    return max(candidates, key=lambda t: t.effective_from).rate


@router.get(
    "",
    response_model=YearSummary,
    description="Годовая сводка стоимости ресурсов. Для расчёта потребления и стоимости используется разница\n    показаний между соседними месяцами с учётом действующих на тот момент тарифов.\n    Для первого месяца года берётся последнее показание предыдущего года как базовая точка.",
)
async def year_summary(year: int = Query(description="Расчётный год (например, 2024)."),
                       db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Reading)
        .where(extract("year", Reading.period) == year)
        .order_by(Reading.period.asc())
    )
    result = await db.execute(stmt)
    readings = list(result.scalars().all())

    # Also need the last reading of previous year as baseline
    prev_stmt = (
        select(Reading)
        .where(extract("year", Reading.period) < year)
        .order_by(Reading.period.desc())
        .limit(1)
    )
    prev_result = await db.execute(prev_stmt)
    prev_reading = prev_result.scalar_one_or_none()

    tariffs_result = await db.execute(select(Tariff))
    tariffs = list(tariffs_result.scalars().all())

    months: list[MonthlyCostRead] = []

    all_readings = ([prev_reading] if prev_reading else []) + readings

    for i in range(1, len(all_readings)):
        prev = all_readings[i - 1]
        curr = all_readings[i]

        tariff = TariffSet(
            hws_rate=_rate_for(tariffs, "hws", curr.period),
            cws_rate=_rate_for(tariffs, "cws", curr.period),
            electric_rate=_rate_for(tariffs, "electric", curr.period),
            rent=_rate_for(tariffs, "rent", curr.period),
        )

        calc = calculate_month(
            current_hws=curr.hws_value,
            current_cws=curr.cws_value,
            current_electric=curr.electric_value,
            previous_hws=prev.hws_value,
            previous_cws=prev.cws_value,
            previous_electric=prev.electric_value,
            tariff=tariff,
        )

        # Note is stored per reading (from the import), carry it into the output
        cost_result = await db.execute(
            select(MonthlyCost.note).where(MonthlyCost.reading_id == curr.id)
        )
        note = cost_result.scalar_one_or_none()

        months.append(MonthlyCostRead(
            period=curr.period,
            hws_consumption=calc.hws_consumption,
            cws_consumption=calc.cws_consumption,
            electric_consumption=calc.electric_consumption,
            hws_cost=calc.hws_cost,
            cws_cost=calc.cws_cost,
            electric_cost=calc.electric_cost,
            rent=calc.rent,
            total=calc.total,
            note=note,
        ))

    return YearSummary(
        year=year,
        months=months,
        total_hws_cost=round(sum(m.hws_cost for m in months), 2),
        total_cws_cost=round(sum(m.cws_cost for m in months), 2),
        total_electric_cost=round(sum(m.electric_cost for m in months), 2),
        total_rent=round(sum(m.rent for m in months), 2),
        grand_total=round(sum(m.total for m in months), 2),
    )


@router.get("/stats", response_model=StatsRead)
async def stats(year: int = Query(description="Расчётный год (например, 2024)."),
                db: AsyncSession = Depends(get_db)):
    summary = await year_summary(year, db)
    totals = [m.total for m in summary.months]

    return StatsRead(
        year=year,
        avg_monthly_total=round(sum(totals) / len(totals), 2) if totals else 0,
        max_month_total=max(totals) if totals else 0,
        min_month_total=min(totals) if totals else 0,
        total_readings=len(totals),
    )