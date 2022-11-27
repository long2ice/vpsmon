import asyncio

from vpsmon.enums import Currency, ProviderType
from vpsmon.models import VPS, DataCenter
from vpsmon.payment import (
    BTC,
    ETH,
    USDT,
    AliPay,
    ApplePay,
    BankTransfer,
    GooglePay,
    Stripe,
)
from vpsmon.providers import Provider


class VPSHosting(Provider):
    type = ProviderType.vps
    icon = "/provider/vps.ico"
    name = "V.PS"
    homepage = "https://v.ps"
    payments = [AliPay, ETH, BTC, USDT, ApplePay, GooglePay, Stripe, BankTransfer]
    aff = 544
    aff_url = f"https://vps.hosting/?affid={aff}"

    @classmethod
    async def get_vps_list(cls) -> list[VPS]:
        url = f"{cls.homepage}/pricing"
        session = cls._get_session()
        r = await session.get(url)
        vps_list = []
        for plan in r.html.find(".plan"):
            name = plan.find("h2", first=True).text
            price = plan.find(".price", first=True).find("span.num", first=True).text
            ps = plan.find("p")
            cpu = ps[0].text.split(" ")[0]
            memory, memory_unit, _ = ps[1].text.split(" ")
            if memory_unit == "GB":
                memory = float(memory) * 1024
            elif memory_unit == "MB":
                memory = float(memory)
            disk, disk_unit = ps[2].text.split(" ")[:2]
            if disk_unit == "GB":
                disk = float(disk)
            elif disk_unit == "TB":
                disk = float(disk) * 1024
            disk_type = " ".join(ps[2].text.split(" ")[2:])
            bandwidth, bandwidth_unit = ps[3].text.split(" ")[:2]
            if bandwidth_unit == "TB":
                bandwidth = float(bandwidth) * 1024
            elif bandwidth_unit == "GB":
                bandwidth = float(bandwidth)
            vps = VPS(
                provider=cls.type,
                category="Pricing",
                name=name,
                price=price,
                currency=Currency.EUR,
                period="month",
                cpu=cpu,
                memory=memory,
                disk=disk,
                disk_type=disk_type,
                bandwidth=bandwidth,
                ipv4=1,
                ipv6=1,
                link=cls.aff_url,
                speed=-1,
                count=-1,
            )
            vps_list.append(vps)
        return vps_list

    @classmethod
    async def _get_datacenter(cls, url: str):
        session = cls._get_session()
        r = await session.get(url)
        card = r.html.find(".card-body", first=True)
        ps = card.find("p")
        name, location = ps[0].find("strong", first=True).text.split(", ")
        ipv4 = ps[1].text.split(" ")[-1]
        ipv6 = ps[2].text.split(" ")[-1]
        datacenter = DataCenter(
            name=name,
            location=location,
            ipv4=ipv4,
            ipv6=ipv6,
            provider=cls.type,
        )
        return datacenter

    @classmethod
    async def get_datacenter_list(cls) -> list[DataCenter]:
        session = cls._get_session()
        r = await session.get("https://v.ps/speedtest")
        table = r.html.find("table", first=True)
        tasks = []
        for i, tr in enumerate(table.find("tr")):
            if i == 0:
                continue
            tds = tr.find("td")
            href = tds[2].find("a", first=True).attrs.get("href")
            tasks.append(asyncio.ensure_future(cls._get_datacenter(href)))
        datacenters = await asyncio.gather(*tasks)
        return list(datacenters)
