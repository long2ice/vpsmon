from enum import Enum


class ProviderType(str, Enum):
    racknerd = "racknerd"
    greencloud = "greencloud"
    hosthatch = "hosthatch"
    pacificrack = "pacificrack"
    cloudcone = "cloudcone"
    digitalvirt = "digitalvirt"
    bandwagonhost = "bandwagonhost"
    dmit = "dmit"
    vultr = "vultr"
    vps = "v.ps"
    advinservers = "advinservers"


class VPSPeriod(str, Enum):
    month = "month"
    year = "year"
    triennium = "triennium"
    quarterly = "quarterly"


class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"
    CNY = "CNY"
