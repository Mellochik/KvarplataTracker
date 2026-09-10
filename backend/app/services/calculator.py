from dataclasses import dataclass


@dataclass(frozen=True)
class TariffSet:
    xvs_rate: float
    gvs_rate: float
    electric_rate: float
    rent: float


@dataclass
class MonthCalculation:
    xvs_consumption: float
    gvs_consumption: float
    electric_consumption: float
    xvs_cost: float
    gvs_cost: float
    electric_cost: float
    rent: float
    total: float


def calculate_month(
    current_xvs: float,
    current_gvs: float,
    current_electric: float,
    previous_xvs: float,
    previous_gvs: float,
    previous_electric: float,
    tariff: TariffSet,
) -> MonthCalculation:
    xvs_consumption = max(current_xvs - previous_xvs, 0)
    gvs_consumption = max(current_gvs - previous_gvs, 0)
    electric_consumption = max(current_electric - previous_electric, 0)

    return MonthCalculation(
        xvs_consumption=xvs_consumption,
        gvs_consumption=gvs_consumption,
        electric_consumption=electric_consumption,
        xvs_cost=round(xvs_consumption * tariff.xvs_rate, 2),
        gvs_cost=round(gvs_consumption * tariff.gvs_rate, 2),
        electric_cost=round(electric_consumption * tariff.electric_rate, 2),
        rent=tariff.rent,
        total=round(
            xvs_consumption * tariff.xvs_rate
            + gvs_consumption * tariff.gvs_rate
            + electric_consumption * tariff.electric_rate
            + tariff.rent,
            2,
        ),
    )
