from enum import Enum


class ProviderType(str, Enum):
    racknerd = "racknerd"
    greencloud = "greencloud"
    licloud = "licloud"


class VPSPeriod(str, Enum):
    month = "month"
    year = "year"


class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"
    CNY = "CNY"
