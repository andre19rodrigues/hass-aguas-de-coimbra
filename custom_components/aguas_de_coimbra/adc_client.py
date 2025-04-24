import logging

from datetime import date
from datetime import datetime
from datetime import timedelta

from aiohttp import ClientSession

from .const import BALCAO_DIGITAL_URL


_LOGGER = logging.getLogger(__name__)


class InvalidAuth(Exception):
    """Raised when authentication fails."""

    pass


class CannotConnect(Exception):
    """Raised when a connection to the API fails."""

    pass


class AdCClient:
    def __init__(self, username: str, password: str, session: ClientSession):
        self._username = username
        self._password = password
        self._codigo_marca = None
        self._codigo_produto = None
        self._subscription_id = None
        self._numero_contador = None
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
                _LOGGER.error("Failed to connect to the API")
                raise CannotConnect("Failed to connect to the API")

            data = await resp.json()
            token = data.get("token")
            self._token = token["token"]
            self._token_expiration_date = token["expirationDate"]

    def _is_token_valid(self):
        """Check if the token is still valid."""
        if self._token and self._token_expiration_date:
            return datetime.now().timestamp() < self._token_expiration_date
        return False

    @property
    async def _headers(self):
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

        headers = await self._headers
        async with self._session.get(subscription_url, headers=headers) as resp:
            if resp.status != 200:
                _LOGGER.error("Failed to fetch subscription ID")
                raise Exception("Failed to fetch subscription ID")

            data = await resp.json()
            self._subscription_id = data[0]["subscriptionId"]

    async def get_meter_details(self) -> dict:
        """Fetch meter details using subscription ID"""

        details_url = f"{BALCAO_DIGITAL_URL}uPortal2/coimbra/leituras/getContadores"

        if not self._subscription_id:
            await self.get_subscription_id()

        query_params = {"subscriptionId": self._subscription_id}
        headers = await self._headers
        async with self._session.get(
            details_url, headers=headers, params=query_params
        ) as resp:
            if resp.status != 200:
                _LOGGER.error("Failed to fetch meter details")
                raise Exception("Failed to fetch meter details")

            data = await resp.json()
            self._codigo_marca = data[0]["chaveContador"]["codigoMarca"]
            self._codigo_produto = data[0]["chaveContador"]["codigoProduto"]
            self._numero_contador = data[0]["chaveContador"]["numeroContador"]
            return data

    async def get_last_meter_reading(self) -> float:
        """Fetch latest meter reading"""
        details = await self.get_meter_details()
        return details[0]["ultimaLeitura"]["leituras"][0]["leitura"]

    async def _get_usage(self, day: str) -> dict:
        """Fetch water usage for a specific day"""

        usage_url = f"{BALCAO_DIGITAL_URL}uPortal2/coimbra/History/consumo/carga"

        query_params = {
            "codigoMarca": self._codigo_marca,
            "codigoProduto": self._codigo_produto,
            "subscriptionId": self._subscription_id,
            "numeroContador": self._numero_contador,
            "initialDate": day,
            "finalDate": day,
        }

        headers = await self._headers
        async with self._session.get(
            usage_url, headers=headers, params=query_params
        ) as resp:
            if resp.status != 200:
                _LOGGER.error("Failed to fetch usage data")
                raise Exception("Failed to fetch usage data")

            data = await resp.json()
            return data

    async def get_consumption(self, today: bool = True) -> float:
        """Get water usage for today or yesterday"""

        day = date.today()
        if not today:
            day = day - timedelta(days=1)

        data = await self._get_usage(day=day.isoformat())

        consumption = 0
        for reading in data:
            consumption += reading["consumption"]
        return consumption
