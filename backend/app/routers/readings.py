from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Reading
from app.schemas import ReadingCreate, ReadingRead, ReadingUpdate

router = APIRouter(prefix="/api/readings", tags=["readings"])


@router.get("/years", response_model=list[int], description="Список годов, за которые есть показания.")
async def list_years(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import func
    stmt = select(func.distinct(func.extract("year", Reading.period)))
    result = await db.execute(stmt)
    years = sorted(int(y) for y in result.scalars().all() if y is not None)
    return years


@router.get(
    "",
    response_model=list[ReadingRead],
    description="Список показаний счётчиков. Показания отсортированы по убыванию периода.\n    Если передан параметр `year`, возвращаются только показания за указанный год.",
)
async def list_readings(
    year: int | None = Query(
        default=None,
        description="Год, за который вернуть показания (например, 2024). Если не указан — все годы.",
    ),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Reading).order_by(Reading.period.desc())
    if year is not None:
        from sqlalchemy import extract
        stmt = stmt.where(extract("year", Reading.period) == year)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "",
    response_model=ReadingRead,
    status_code=201,
    description="Добавить новые показания счётчиков за расчётный период. Период должен быть уникальным.",
    responses={
        409: {
            "description": "Показания за данный период уже существуют",
            "content": {
                "application/json": {"example": {"detail": "Reading for 2024-12-01 already exists"}}
            },
        }
    },
)
async def create_reading(payload: ReadingCreate, db: AsyncSession = Depends(get_db)):
    # Check for duplicate period
    existing = await db.execute(select(Reading).where(Reading.period == payload.period))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Reading for {payload.period} already exists")

    reading = Reading(**payload.model_dump())
    db.add(reading)
    await db.commit()
    await db.refresh(reading)
    return reading


@router.put(
    "/{reading_id}",
    response_model=ReadingRead,
    description="Обновить показания счётчиков (период, поля ХВС, ГВС и электроэнергии) по идентификатору записи.",
    responses={
        404: {
            "description": "Запись показаний с указанным идентификатором не найдена",
            "content": {"application/json": {"example": {"detail": "Reading not found"}}},
        },
        409: {
            "description": "Показания за указанный период уже существуют",
            "content": {
                "application/json": {"example": {"detail": "Reading for 2024-12-01 already exists"}}
            },
        },
    },
)
async def update_reading(reading_id: int, payload: ReadingUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Reading).where(Reading.id == reading_id))
    reading = result.scalar_one_or_none()
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")

    if payload.period != reading.period:
        existing = await db.execute(
            select(Reading).where(Reading.period == payload.period, Reading.id != reading_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=409, detail=f"Reading for {payload.period} already exists")

    for key, value in payload.model_dump().items():
        setattr(reading, key, value)
    await db.commit()
    await db.refresh(reading)
    return reading


@router.delete(
    "/{reading_id}",
    status_code=204,
    description="Удалить запись показаний счётчиков по идентификатору. При успешном удалении возвращается пустой ответ.",
    responses={
        404: {
            "description": "Запись показаний с указанным идентификатором не найдена",
            "content": {"application/json": {"example": {"detail": "Reading not found"}}},
        }
    },
)
async def delete_reading(reading_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Reading).where(Reading.id == reading_id))
    reading = result.scalar_one_or_none()
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")

    await db.delete(reading)
    await db.commit()
