from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Tariff(Base):
    __tablename__ = "tariffs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resource_type: Mapped[str] = mapped_column(String(20), nullable=False)  # hws, cws, electric
    rate: Mapped[float] = mapped_column(Float, nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)


class Reading(Base):
    __tablename__ = "readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    period: Mapped[date] = mapped_column(Date, unique=True, nullable=False)
    hws_value: Mapped[float] = mapped_column(Float, nullable=False)
    cws_value: Mapped[float] = mapped_column(Float, nullable=False)
    electric_value: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    cost: Mapped["MonthlyCost | None"] = relationship(back_populates="reading", uselist=False)


class MonthlyCost(Base):
    __tablename__ = "monthly_costs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reading_id: Mapped[int] = mapped_column(Integer, ForeignKey("readings.id"), unique=True, nullable=False)
    hws_cost: Mapped[float] = mapped_column(Float, nullable=False)
    cws_cost: Mapped[float] = mapped_column(Float, nullable=False)
    electric_cost: Mapped[float] = mapped_column(Float, nullable=False)
    rent: Mapped[float] = mapped_column(Float, nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)

    reading: Mapped["Reading"] = relationship(back_populates="cost")
