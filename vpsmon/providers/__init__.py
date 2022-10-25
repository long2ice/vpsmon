import abc
import ipaddress
from typing import Optional, Type

from requests_html import AsyncHTMLSession

from vpsmon.enums import ProviderType
from vpsmon.models import VPS, DataCenter
from vpsmon.payment import Payment


class Provider(abc.ABC):
    type: ProviderType
    name: str
    homepage: str
    icon: str
    payments: list[Type[Payment]]
    aff_url: str
    timeout = 30
    datacenter_url: str
    aff: int

    @classmethod
    def dict(cls):
        return {
            "type": cls.type,
            "name": cls.name,
            "homepage": cls.aff_url,
            "icon": cls.icon,
            "payments": [payment.dict() for payment in cls.payments],
            "datacenter_url": cls.datacenter_url,
        }

    @classmethod
    @abc.abstractmethod
    async def get_vps_list(cls) -> list[VPS]:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    async def get_datacenter_list(cls) -> list[DataCenter]:
        raise NotImplementedError

    @classmethod
    def _get_session(cls) -> AsyncHTMLSession:
        return AsyncHTMLSession()

    @classmethod
    def _check_ipv4(cls, ipv4: str):
        if not ipv4:
            return None
        try:
            ipaddress.ip_address(ipv4)
            return ipv4
        except ValueError:
            return None

    @classmethod
    def _check_ipv6(cls, ipv6: Optional[str]):
        if not ipv6:
            return None
        try:
            ipaddress.ip_address(ipv6)
            return ipv6
        except ValueError:
            return None
