from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import engine
from app.models import Base
from app.routers import export, readings, summary, tariffs


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (for initial setup; use Alembic in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="KvarplataTracker API",
    description=(
        "API для учёта коммунальных платежей и расчёта стоимости ресурсов на домашнем сервере.\n\n"
        "Позволяет вести показания счётчиков (горячая/холодная вода, электроэнергия),\n"
        "управлять тарифами и получать годовые сводки и статистику стоимости.\n\n"
        "Сокращения: **hws** — горячая вода, **cws** — холодная вода, **electric** — электроэнергия,\n"
        "**rent** — аренда/наём."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(readings.router)
app.include_router(tariffs.router)
app.include_router(summary.router)
app.include_router(export.router)


@app.get(
    "/health",
    description="Проверка работоспособности сервиса. Возвращает статус сервиса.",
    summary="Проверка здоровья сервиса",
)
async def health():
    return {"status": "ok"}
