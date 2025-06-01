from .const import (
    WATER_FIXED_FEE,
    WATER_FIXED_FEE__SOCIAL_TARIFF,
    WATER_CONSUMPTION,
    WATER_CONSUMPTION__SOCIAL_TARIFF,
    WATER_RESOURCES_TAX,
    SEWAGE_FIXED_FEE,
    SEWAGE_FIXED_FEE__SOCIAL_TARIFF,
    SEWAGE_CONSUMPTION,
    SEWAGE_CONSUMPTION__SOCIAL_TARIFF,
    SEWAGE_RESOURCES_TAX,
    SOLID_WASTE_FIXED_FEE,
    SOLID_WASTE_FIXED_FEE__SOCIAL_TARIFF,
    SOLID_WASTE_CONSUMPTION,
    SOLID_WASTE_CONSUMPTION__SOCIAL_TARIFF,
    SOLID_WASTE_MANAGEMENT_TAX,
)


def calculate_water_consumption_cost(
    consumption_m3: float, social_tariff: bool = False
) -> float:

    water_cost = 0
    remaining = consumption_m3

    if social_tariff:
        for tier in WATER_CONSUMPTION__SOCIAL_TARIFF:
            if remaining <= 0:
                break
            if remaining > tier["max"]:
                water_cost += tier["price"] * (tier["max"] - tier["min"])
                remaining -= tier["max"] - tier["min"]
            else:
                water_cost += tier["price"] * (remaining)
                remaining = 0
    else:
        for tier in WATER_CONSUMPTION:
            if remaining <= 0:
                break
            if remaining > tier["max"]:
                water_cost += tier["price"] * (tier["max"] - tier["min"])
                remaining -= tier["max"] - tier["min"]
            else:
                water_cost += tier["price"] * (remaining)
                remaining = 0
    return water_cost


def calculate_water_fixed_fee_cost(
    days_in_cycle: int, social_tariff: bool = False, diameter: int = 15
) -> float:

    if not social_tariff:
        for elem in WATER_FIXED_FEE:
            if diameter >= elem["min"] and diameter < elem["max"]:
                return elem["price"] * days_in_cycle

    return WATER_FIXED_FEE__SOCIAL_TARIFF * days_in_cycle


def calculate_sewage_cost(
    water_cost: float, days_in_cycle: int, social_tariff: bool = False
) -> float:

    sewage_cost = 0
    if social_tariff:
        sewage_cost += SEWAGE_FIXED_FEE__SOCIAL_TARIFF * days_in_cycle
        sewage_cost += SEWAGE_CONSUMPTION__SOCIAL_TARIFF * water_cost
    else:
        sewage_cost += SEWAGE_FIXED_FEE * days_in_cycle
        sewage_cost += SEWAGE_CONSUMPTION * water_cost
    return sewage_cost


def calculate_solid_waste_cost(
    consumption_m3: float, days_in_cycle: int, social_tariff: bool = False
) -> float:

    solid_waste_cost = 0
    if social_tariff:
        solid_waste_cost += SOLID_WASTE_FIXED_FEE__SOCIAL_TARIFF * days_in_cycle
        solid_waste_cost += SOLID_WASTE_CONSUMPTION__SOCIAL_TARIFF * consumption_m3
    else:
        solid_waste_cost += SOLID_WASTE_FIXED_FEE * days_in_cycle
        solid_waste_cost += SOLID_WASTE_CONSUMPTION * consumption_m3
    solid_waste_cost += SOLID_WASTE_MANAGEMENT_TAX * consumption_m3
    return solid_waste_cost


def calculate_taxes_cost(
    consumption_m3: float,
    days_in_cycle: int,
) -> float:

    water_taxes = WATER_RESOURCES_TAX * consumption_m3
    sewage_taxes = SEWAGE_RESOURCES_TAX * consumption_m3
    return water_taxes + sewage_taxes
