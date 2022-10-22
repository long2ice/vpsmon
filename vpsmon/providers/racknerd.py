import asyncio
import itertools
import re

from requests_html import AsyncHTMLSession

from vpsmon.models import VPS, DataCenter
from vpsmon.payment import BTC, AliPay, CreditCard, PayPal
from vpsmon.providers import Provider, ProviderType


class RackNerd(Provider):
    type = ProviderType.racknerd
    icon = "https://www.racknerd.com/favicon.png"
    name = "RackNerd"
    homepage = "https://www.racknerd.com"
    payments = [PayPal, CreditCard, AliPay, BTC]
    datacenter_url = "https://www.racknerd.com/datacenters"
    aff = 5797
    aff_url = f"https://my.racknerd.com/aff.php?aff={aff}"

    @classmethod
    async def _get_vps_list(cls, category: str, path: str):
        url = f"{cls.homepage}{path}"
        session = cls._get_session()
        r = await session.get(url)
        vps_list = []
        for i, tr in enumerate(r.html.find("table tr")):
            if i == 0:
                continue
            tds = tr.find("td")
            name = tds[0].text
            if not name:
                continue
            memory, memory_unit, _ = name.split(" ")
            if memory_unit == "GB":
                memory = int(memory) * 1024
            elif memory_unit == "MB":
                memory = int(memory)
            cpu = tds[1].text.split(" ")[0]
            disk, dist_unit = tds[2].find("b", first=True).text.split(" ")
            if dist_unit == "GB":
                disk = int(disk)
            elif dist_unit == "TB":
                disk = int(disk) * 1024
            disk_type = tds[2].text.split(" GB ")[1]
            bandwidth = tds[3].text
            bandwidth_items = bandwidth.split(" @ ")
            bandwidth, bandwidth_unit = bandwidth_items[0].split(" ")
            if bandwidth_unit == "TB":
                bandwidth = int(bandwidth) * 1024
            elif bandwidth_unit == "GB":
                bandwidth = int(bandwidth)
            speed = bandwidth_items[1]
            if speed.endswith("Gbps"):
                speed = speed.split("Gbps")[0]
                speed = int(speed) * 1024
            ipv4 = tds[4].text.split(" ")[0]
            price, period = tds[5].text.split(" ")
            price = float(price.split("$")[1])
            currency = "USD"
            period = period.split("/")[1]
            pid = tds[6].find("a", first=True).attrs["href"].split("pid=")[1]
            link = cls.aff_url + f"&pid={pid}"
            vps = VPS(
                name=name,
                category=category,
                provider=cls.type,
                memory=memory,
                cpu=cpu,
                disk=disk,
                disk_type=disk_type,
                bandwidth=bandwidth,
                speed=speed,
                price=price,
                currency=currency,
                ipv4=ipv4,
                period=period,
                link=link,
            )
            vps_list.append(vps)
        return vps_list

    @classmethod
    async def _get_specials(cls):
        url = f"{cls.homepage}/specials"
        session = cls._get_session()
        r = await session.get(url)
        h3 = r.html.find("h3", first=True)
        category = h3.text
        plan_list = r.html.find("div.plan-listing", first=True)
        vps_list = []
        for plan_box in plan_list.find("div.plan-box"):
            name = plan_box.find("h3", first=True).text
            price = plan_box.find("div.price", first=True).text
            price = float(price.split("$")[1])
            currency = "USD"
            period = plan_box.find("span.per", first=True).text
            _, period = period.split(" ")
            if period == "YEAR":
                period = "year"
            elif period == "MONTH":
                period = "month"
            lis = plan_box.find("ul li")
            cpu = lis[0].text.split(" ")[0]
            disk = lis[1].text.split(" ")[0]
            disk_type = lis[1].text.split(" GB ")[1]
            memory, unit, _ = lis[2].text.split(" ")
            if unit == "GB":
                memory = int(memory) * 1024
            elif unit == "MB":
                memory = int(memory)
            bandwidth, unit, _, _ = lis[3].text.split(" ")
            if unit == "TB":
                bandwidth = float(bandwidth) * 1024
            elif unit == "GB":
                bandwidth = float(bandwidth)
            speed = lis[4].text.split(" ")[0]
            if speed.endswith("Gbps"):
                speed = speed.split("Gbps")[0]
                speed = int(speed) * 1024
            ipv4 = lis[6].text.split(" ")[0]
            href = plan_box.find("a", first=True).attrs["href"]
            pid = href.split("pid=")[1]
            link = cls.aff_url + f"&pid={pid}"
            vps = VPS(
                name=name,
                category=category,
                provider=cls.type,
                memory=memory,
                cpu=cpu,
                disk=disk,
                disk_type=disk_type,
                bandwidth=bandwidth,
                speed=speed,
                price=price,
                currency=currency,
                ipv4=ipv4,
                period=period,
                link=link,
            )
            vps_list.append(vps)
        return vps_list

    @classmethod
    async def get_vps_list(cls) -> list[VPS]:
        tasks = [
            asyncio.ensure_future(cls._get_vps_list("KVM VPS", "/kvm-vps")),
            asyncio.ensure_future(cls._get_vps_list("AMD Ryzen VPS", "/ryzen-vps")),
            asyncio.ensure_future(cls._get_vps_list("Windows VPS", "/windows-vps")),
            asyncio.ensure_future(cls._get_specials()),
        ]
        vps_list = await asyncio.gather(*tasks)
        return list(itertools.chain(*vps_list))

    @classmethod
    async def _get_datacenter_ip(cls, session: AsyncHTMLSession, link: str):
        r = await session.get(link)
        li = r.html.find(".specbox ul li")
        try:
            ipv4 = li[4].text.split(" ")[-1]
        except IndexError:
            ipv4 = None
        return cls._check_ipv4(ipv4)

    @classmethod
    async def get_datacenter_list(cls) -> list[DataCenter]:
        session = cls._get_session()
        r = await session.get(cls.datacenter_url)
        box = r.html.find(".location-box")
        datacenters = []
        for b in box:
            p = b.find("p")
            name = p[0].text
            location = p[1].text
            input_ = b.find("input", first=True)
            onclick = input_.attrs["onclick"]
            link = re.findall(r"\'(.*)\'", onclick)[0]
            ipv4 = await cls._get_datacenter_ip(session, link)
            datacenters.append(
                DataCenter(
                    provider=cls.type,
                    name=name,
                    location=location,
                    ipv4=ipv4,
                )
            )
        return datacenters
