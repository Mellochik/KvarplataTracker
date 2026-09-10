from datetime import date

from pydantic import BaseModel, Field

# --- Tariff ---

class TariffRead(BaseModel):
    """Тариф для расчётного ресурса."""

    id: int = Field(description="Уникальный идентификатор тарифа")
    resource_type: str = Field(description="Тип ресурса: hws — горячая вода, cws — холодная вода, electric — электричество, rent — аренда/наём")
    rate: float = Field(description="Значение тарифа (стоимость за единицу)")
    effective_from: date = Field(description="Дата начала действия тарифа")
    effective_to: date | None = Field(default=None, description="Дата окончания действия тарифа (null — тариф текущий)")


class TariffUpdate(BaseModel):
    """Данные для создания нового или обновления текущего тарифа."""

    resource_type: str = Field(description="Тип ресурса: hws, cws, electric, rent")
    rate: float = Field(gt=0, description="Значение тарифа, должно быть больше 0")
    effective_from: date = Field(description="Дата начала действия тарифа")


# --- Reading ---

class ReadingCreate(BaseModel):
    """Данные для добавления новых показаний счётчиков."""

    period: date = Field(description="Расчётный период (месяц), должен быть уникальным")
    hws_value: float = Field(ge=0, description="Показание счётчика горячей воды (ГВС)")
    cws_value: float = Field(ge=0, description="Показание счётчика холодной воды (ХВС)")
    electric_value: float = Field(ge=0, description="Показание счётчика электроэнергии")


class ReadingUpdate(BaseModel):
    """Данные для обновления показаний счётчиков."""

    hws_value: float = Field(ge=0, description="Показание счётчика горячей воды (ГВС)")
    cws_value: float = Field(ge=0, description="Показание счётчика холодной воды (ХВС)")
    electric_value: float = Field(ge=0, description="Показание счётчика электроэнергии")


class ReadingRead(BaseModel):
    """Показания счётчиков за расчётный период."""

    id: int = Field(description="Уникальный идентификатор записи показаний")
    period: date = Field(description="Расчётный период (месяц)")
    hws_value: float = Field(description="Показание счётчика горячей воды (ГВС)")
    cws_value: float = Field(description="Показание счётчика холодной воды (ХВС)")
    electric_value: float = Field(description="Показание счётчика электроэнергии")


# --- Monthly Cost / Summary ---

class MonthlyCostRead(BaseModel):
    """Стоимость ресурсов за один расчётный месяц."""

    period: date = Field(description="Расчётный месяц")
    hws_consumption: float = Field(description="Объём потребления горячей воды (м³)")
    cws_consumption: float = Field(description="Объём потребления холодной воды (м³)")
    electric_consumption: float = Field(description="Объём потребления электроэнергии (кВт·ч)")
    hws_cost: float = Field(description="Стоимость горячей воды за месяц")
    cws_cost: float = Field(description="Стоимость холодной воды за месяц")
    electric_cost: float = Field(description="Стоимость электроэнергии за месяц")
    rent: float = Field(description="Стоимость аренды/наёма за месяц")
    total: float = Field(description="Итоговая стоимость за месяц (сумма всех составляющих)")
    note: str | None = Field(default=None, description="Примечание к месяцу (может отсутствовать)")


class YearSummary(BaseModel):
    """Сводка стоимости ресурсов за год."""

    year: int = Field(description="Расчётный год")
    months: list[MonthlyCostRead] = Field(description="Детализация по месяцам")
    total_hws_cost: float = Field(description="Суммарная стоимость горячей воды за год")
    total_cws_cost: float = Field(description="Суммарная стоимость холодной воды за год")
    total_electric_cost: float = Field(description="Суммарная стоимость электроэнергии за год")
    total_rent: float = Field(description="Суммарная стоимость аренды/наёма за год")
    grand_total: float = Field(description="Общая сумма за год по всем статьям")


class StatsRead(BaseModel):
    """Статистика ежемесячных затрат за год."""

    year: int = Field(description="Расчётный год")
    avg_monthly_total: float = Field(description="Средний итог по месяцам")
    max_month_total: float = Field(description="Максимальный итог по месяцам")
    min_month_total: float = Field(description="Минимальный итог по месяцам")
    total_readings: int = Field(description="Количество месяцев с расчётом в году")
