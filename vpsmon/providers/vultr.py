import asyncio

from vpsmon.enums import ProviderType
from vpsmon.models import VPS, DataCenter
from vpsmon.payment import BTC, ETH, AliPay, CreditCard, PayPal, UnionPay, WireTransfer
from vpsmon.providers import Provider


class Vultr(Provider):
    type = ProviderType.vultr
    icon = "/vultr.png"
    name = "Vultr"
    homepage = "https://www.vultr.com"
    payments = [PayPal, AliPay, ETH, CreditCard, BTC, WireTransfer, UnionPay]
    datacenter_url = "https://www.vultr.com/features/datacenter-locations/"
    aff = 5324
    aff_url = f"https://www.dmit.io/aff.php?aff={aff}"

    @classmethod
    async def get_vps_list(cls) -> list[VPS]:
        url = f"{cls.homepage}/pricing"
        session = cls._get_session()
        r = await session.get(url)
        vps_list = []
        cloud_compute = r.html.find("#cloud-compute", first=True)
        optimized_cloud_compute = r.html.find("#optimized-cloud-compute", first=True)
        for item in [cloud_compute, optimized_cloud_compute]:
            for pricing in item.find(".pricing__subsection"):
                category = pricing.find(".pricing__subsection-title", first=True).text
                pt__body = pricing.find(".pt__body", first=True)
                for row in pt__body.find(".pt__row"):
                    pt__cell = row.find(".pt__cell")
                    cpu = pt__cell[0].find("strong", first=True).text
                    memory, memory_unit = pt__cell[1].text.split(" ")[0].split("\xa0")
                    if memory_unit == "GB":
                        memory = float(memory) * 1024
                    bandwidth, bandwidth_unit = pt__cell[2].text.split(" ")[0].split("\xa0")
                    if bandwidth_unit == "TB":
                        bandwidth = float(bandwidth) * 1024
                    disk, disk_unit = pt__cell[3].text.split(" ")[0].split("\xa0")
                    if disk_unit == "TB":
                        disk = float(bandwidth) * 1024
                    price, price_unit = pt__cell[4].text.split(" ")
                    price = price.split("$")[1].replace(",", "")
                    vps = VPS(
                        provider=cls.type,
                        category=category,
                        name=f"{cpu} CPU {memory} RAM",
                        price=price,
                        currency="USD",
                        period="month",
                        cpu=cpu,
                        memory=memory,
                        disk=disk,
                        disk_type="SSD",
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
    async def _get_datacenter(cls, a):
        session = cls._get_session()
        href = a.attrs["href"]
        name = a.find(".location__title", first=True).text
        location = a.find(".location__desc", first=True).text
        ret = await session.get(href, timeout=cls.timeout)
        ipv4 = ret.html.find("#useripv4", first=True).text
        ipv6 = ret.html.find("#useripv6", first=True).text
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
        r = await session.get(cls.datacenter_url)
        slider = r.html.find(".full-width-slider__slider", first=True)
        tasks = []
        for a in slider.find("a"):
            tasks.append(asyncio.ensure_future(cls._get_datacenter(a)))
        datacenters = await asyncio.gather(*tasks)
        return list(datacenters)
