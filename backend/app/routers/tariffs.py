from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Tariff
from app.schemas import TariffRead, TariffUpdate

router = APIRouter(prefix="/api/tariffs", tags=["tariffs"])


@router.get(
    "",
    response_model=list[TariffRead],
    description="Список всех тарифов, отсортированных по убыванию даты начала действия.\n    Для каждого ресурса показывается история тарифов, включая действующий (поле `effective_to` равно null).",
)
async def list_tariffs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tariff).order_by(Tariff.effective_from.desc()))
    return result.scalars().all()


@router.put(
    "",
    response_model=TariffRead,
    description="Создать новый тариф или обновить действующий для заданного типа ресурса.\n    Если для указанного типа уже есть действующий тариф, его срок закрывается (поле `effective_to`\n    устанавливается на сегодняшний день), и создаётся новый тариф с указанной ставкой.",
)
async def upsert_tariff(payload: TariffUpdate, db: AsyncSession = Depends(get_db)):
    """Создать новый тариф или обновить текущий для заданного типа ресурса."""
    stmt = (
        select(Tariff)
        .where(
            Tariff.resource_type == payload.resource_type,
            Tariff.effective_to.is_(None),
        )
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        # Close the previous tariff period
        existing.effective_to = date.today()
        db.add(existing)

    new_tariff = Tariff(
        resource_type=payload.resource_type,
        rate=payload.rate,
        effective_from=payload.effective_from,
    )
    db.add(new_tariff)
    await db.commit()
    await db.refresh(new_tariff)
    return new_tariff
