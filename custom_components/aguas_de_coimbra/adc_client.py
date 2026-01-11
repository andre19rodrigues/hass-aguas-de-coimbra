import logging
from datetime import timedelta

from aiohttp import ClientSession
from homeassistant.util import dt as dt_util

from .const import BALCAO_DIGITAL_URL, VAT_RATE
from .utils import (
    calculate_water_consumption_cost,
    calculate_water_fixed_fee_cost,
    calculate_sewage_cost,
    calculate_solid_waste_cost,
    calculate_taxes_cost,
)

_LOGGER = logging.getLogger(__name__)


class InvalidAuth(Exception):
    """Raised when authentication fails."""

    pass


class CannotConnect(Exception):
    """Raised when a connection to the API fails."""

    pass


class AdCClient:
    def __init__(
        self,
        username: str,
        password: str,
        billing_cycle_start_day: int,
        social_tariff: bool,
        session: ClientSession,
    ):
        self._username = username
        self._password = password
        self._billing_cycle_start_day = billing_cycle_start_day
        self._social_tariff = social_tariff
        self._codigo_marca = None
        self._codigo_produto = None
        self._subscription_id = None
        self._numero_contador = None
        self._diameter = None
        self._token = None
        self._token_expiration_date = None
        self._session = session

    async def login(self):
        """Login to the Aguas de Coimbra portal."""
        login_url = f"{BALCAO_DIGITAL_URL}uPortal2/coimbra/login"
        payload = {
            "username": self._username,
            "password": self._password,
        }

        async with self._session.post(login_url, json=payload) as resp:
            if resp.status == 401:
                _LOGGER.error("Invalid username or password")
                raise InvalidAuth("Invalid username or password")
            elif resp.status != 200:
                _LOGGER.error("Failed to connect to the API. Status code: %s", resp.status)
                raise CannotConnect("Failed to connect to the API")

            data = await resp.json()
            token = data.get("token")
            self._token = token["token"]
            self._token_expiration_date = token["expirationDate"]

    def _is_token_valid(self):
        """Check if the token is still valid."""
        if self._token and self._token_expiration_date:
            return dt_util.now().timestamp() < self._token_expiration_date
        return False

    async def _headers(self) -> dict:
        """Set headers for subsequent requests."""
        if not self._is_token_valid():
            _LOGGER.debug("Token expired, logging in again")
            await self.login()

        return {
            "X-Auth-Token": self._token,
            "Content-Type": "application/json",
        }

    async def get_subscription_id(self) -> list:
        """Fetch account subscription ID"""

        subscription_url = (
            f"{BALCAO_DIGITAL_URL}uPortal2/coimbra/Subscription/listSubscriptions"
        )

        headers = await self._headers()
        async with self._session.get(subscription_url, headers=headers) as resp:
            if resp.status != 200:
                _LOGGER.error("Failed to fetch subscription ID. Status code: %s", resp.status)
                raise Exception("Failed to fetch subscription ID")

            data = await resp.json()
            self._subscription_id = data[0]["subscriptionId"]

    async def get_meter_details(self) -> dict:
        """Fetch meter details using subscription ID"""

        details_url = f"{BALCAO_DIGITAL_URL}uPortal2/coimbra/leituras/getContadores"

        if not self._subscription_id:
            await self.get_subscription_id()

        query_params = {"subscriptionId": self._subscription_id}
        headers = await self._headers()
        async with self._session.get(
            details_url, headers=headers, params=query_params
        ) as resp:
            if resp.status != 200:
                _LOGGER.error("Failed to fetch meter details. Status code: %s", resp.status)
                # revoke token if it fails
                self._token = None
                raise Exception("Failed to fetch meter details")

            data = await resp.json()
            self._codigo_marca = data[0]["chaveContador"]["codigoMarca"]
            self._codigo_produto = data[0]["chaveContador"]["codigoProduto"]
            self._numero_contador = data[0]["chaveContador"]["numeroContador"]

            try:
                diameter = data[0]["descModelo"]
                diameter = diameter.split("/")[1].strip()
                diameter = int(diameter)
            except (IndexError, ValueError):
                _LOGGER.warning(
                    "Could not parse diameter from model description, using default value (15mm)"
                )
                # If the diameter cannot be parsed, set a default value
                diameter = 15
            self._diameter = diameter
            return data

    async def get_last_meter_reading(self) -> float:
        """Fetch latest meter reading"""
        details = await self.get_meter_details()
        return details[0]["ultimaLeitura"]["leituras"][0]["leitura"]

    async def _get_usage(self, initial_day: str, final_day: str = None) -> dict:
        """Fetch water usage for a specific day"""

        usage_url = f"{BALCAO_DIGITAL_URL}uPortal2/coimbra/History/consumo/carga"

        if not self._subscription_id:
            await self.get_subscription_id()
        if (
            not self._codigo_marca
            or not self._codigo_produto
            or not self._numero_contador
        ):
            await self.get_meter_details()

        query_params = {
            "codigoMarca": self._codigo_marca,
            "codigoProduto": self._codigo_produto,
            "subscriptionId": self._subscription_id,
            "numeroContador": self._numero_contador,
            "initialDate": initial_day,
            "finalDate": final_day if final_day else initial_day,
        }

        headers = await self._headers()
        async with self._session.get(
            usage_url, headers=headers, params=query_params
        ) as resp:
            if resp.status != 200:
                _LOGGER.error("Failed to fetch usage data. Status code: %s", resp.status)
                raise Exception("Failed to fetch usage data")

            data = await resp.json()
            return data

    async def get_consumption_day(self, today: bool = True) -> float:
        """Get water usage for a day. Today or yesterday"""

        day = dt_util.now()
        if not today:
            day = day - timedelta(days=1)

        data = await self._get_usage(initial_day=day.strftime("%Y-%m-%d"))

        consumption = 0
        for reading in data:
            consumption += reading["consumption"]
        return consumption

    def _get_billing_cycle_dates(self) -> tuple:
        """Get the start and end dates of the current billing cycle"""
        now = dt_util.now()
        if now.day < self._billing_cycle_start_day:
            # If today is before the billing cycle start, use last month
            month = now.month - 1 if now.month > 1 else 12
            year = now.year if month != 12 else now.year - 1
        else:
            month = now.month
            year = now.year

        initial_day = f"{year}-{month:02d}-{self._billing_cycle_start_day:02d}"
        final_day = now.strftime("%Y-%m-%d")
        return initial_day, final_day

    async def get_consumption_billing_cycle(self) -> float:
        """Get water usage for the current billing cycle"""

        initial_day, final_day = self._get_billing_cycle_dates()
        data = await self._get_usage(initial_day=initial_day, final_day=final_day)

        consumption = 0
        for reading in data:
            consumption += reading["consumption"]
        return round(consumption / 1000, 2)  # Convert liters to cubic meters

    def calculate_cost(self, billing_cycle_consumption: float) -> float:
        """Calculate the cost for the billing cycle based on consumption"""

        initial_day, final_day = self._get_billing_cycle_dates()
        days_in_cycle = (
            dt_util.parse_datetime(final_day) - dt_util.parse_datetime(initial_day)
        ).days + 1

        consumption_m3 = int(billing_cycle_consumption)

        water_consumption_cost = calculate_water_consumption_cost(
            consumption_m3=consumption_m3, social_tariff=self._social_tariff
        )
        water_fixed_fee_cost = calculate_water_fixed_fee_cost(
            days_in_cycle=days_in_cycle,
            social_tariff=self._social_tariff,
            diameter=self._diameter,
        )
        sewage_cost = calculate_sewage_cost(
            water_cost=water_consumption_cost,
            days_in_cycle=days_in_cycle,
            social_tariff=self._social_tariff,
        )
        solid_waste_cost = calculate_solid_waste_cost(
            consumption_m3=consumption_m3,
            days_in_cycle=days_in_cycle,
            social_tariff=self._social_tariff,
        )
        taxes_cost = calculate_taxes_cost(
            consumption_m3=consumption_m3, days_in_cycle=days_in_cycle
        )

        # Add VAT
        total_cost = (
            water_consumption_cost * (1 + VAT_RATE)
            + water_fixed_fee_cost * (1 + VAT_RATE)
            + sewage_cost * (1 + VAT_RATE)
            + solid_waste_cost  # Solid waste is exempt from VAT
            + taxes_cost * (1 + VAT_RATE)
        )
        return round(total_cost, 2)
