from dataclasses import dataclass


@dataclass(frozen=True)
class TariffSet:
    hws_rate: float
    cws_rate: float
    electric_rate: float
    rent: float


@dataclass
class MonthCalculation:
    hws_consumption: float
    cws_consumption: float
    electric_consumption: float
    hws_cost: float
    cws_cost: float
    electric_cost: float
    rent: float
    total: float


def calculate_month(
    current_hws: float,
    current_cws: float,
    current_electric: float,
    previous_hws: float,
    previous_cws: float,
    previous_electric: float,
    tariff: TariffSet,
) -> MonthCalculation:
    hws_consumption = max(current_hws - previous_hws, 0)
    cws_consumption = max(current_cws - previous_cws, 0)
    electric_consumption = max(current_electric - previous_electric, 0)

    return MonthCalculation(
        hws_consumption=hws_consumption,
        cws_consumption=cws_consumption,
        electric_consumption=electric_consumption,
        hws_cost=round(hws_consumption * tariff.hws_rate, 2),
        cws_cost=round(cws_consumption * tariff.cws_rate, 2),
        electric_cost=round(electric_consumption * tariff.electric_rate, 2),
        rent=tariff.rent,
        total=round(
            hws_consumption * tariff.hws_rate
            + cws_consumption * tariff.cws_rate
            + electric_consumption * tariff.electric_rate
            + tariff.rent,
            2,
        ),
    )
