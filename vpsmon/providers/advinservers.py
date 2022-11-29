import asyncio
import itertools
import re

from vpsmon.enums import ProviderType
from vpsmon.models import VPS, DataCenter
from vpsmon.payment import BTC, ETH, PayPal, Stripe
from vpsmon.providers import Provider


class AdvinServers(Provider):
    type = ProviderType.advinservers
    icon = "/provider/advinservers.png"
    name = "AdvinServers"
    homepage = "https://clients.advinservers.com"
    payments = [PayPal, Stripe, BTC, ETH]
    datacenter_url = ""
    aff = 226
    aff_url = f"https://clients.advinservers.com/aff.php?aff={aff}"

    @classmethod
    async def _get_vps_list(cls, url: str, category: str):
        session = cls._get_session()
        r = await session.get(url, timeout=cls.timeout)
        vps_list = []
        for package in r.html.find("div.package"):
            pid = package.attrs["id"]
            pid = pid.split("product")[1]
            link = f"{cls.homepage}/cart.php?a=add&pid={pid}&aff={cls.aff}"
            name = package.find("h3", first=True).text
            price = package.find("div.price-amount", first=True).text
            price = float(price.split("$")[1])
            period = package.find("div.price-cycle", first=True).text.strip()
            if period == "Monthly":
                period = "month"
            elif period == "Yearly":
                period = "year"
            package_content = package.find("div.package-content p", first=True).text
            items = package_content.split("\n")
            cpu = re.findall(r"\d+", items[0])
            if not cpu:
                continue
            cpu = cpu[0]
            memory = items[1].split(" ")[0]
            if memory.endswith("GB"):
                memory = float(memory.split("GB")[0]) * 1024
            elif memory.endswith("MB"):
                memory = float(memory.split("MB")[0])
            disk = items[2].split(" ")[0]
            if disk.endswith("GB"):
                disk = float(disk.split("GB")[0])
            elif disk.endswith("TB"):
                disk = float(disk.split("TB")[0]) * 1024
            disk_type = " ".join(items[2].split(" ")[1:])
            bandwidth = items[3].split(" ")[0]
            if bandwidth.endswith("GB"):
                bandwidth = float(bandwidth.split("GB")[0])
            elif bandwidth.endswith("TB"):
                bandwidth = float(bandwidth.split("TB")[0]) * 1024
            elif bandwidth == "Unmetered":
                bandwidth = -1
            try:
                speed = int(re.findall(r"(\d+) Gbps", items[3])[0])
            except IndexError:
                speed = -1
            package_qty = package.find("div.package-qty", first=True)
            if package_qty:
                count = int(package_qty.text.split(" ")[0])
            else:
                count = -1
            remarks = items[4]
            vps_list.append(
                VPS(
                    provider=cls.type,
                    category=category,
                    name=name,
                    price=price,
                    cpu=cpu,
                    memory=memory,
                    disk=disk,
                    bandwidth=bandwidth,
                    disk_type=disk_type,
                    period=period,
                    ipv4=1,
                    remarks=remarks,
                    count=count,
                    link=link,
                    speed=speed * 1024,
                )
            )
        return vps_list

    @classmethod
    async def get_vps_list(cls) -> list[VPS]:
        session = cls._get_session()
        r = await session.get(cls.homepage + "/store", timeout=cls.timeout)
        tasks = []
        list_group = r.html.find("div.list-group", first=True)
        for a in list_group.find("a"):
            category = a.attrs["menuitemname"]
            if "KVM" not in category:
                continue
            href = a.attrs["href"]
            tasks.append(asyncio.ensure_future(cls._get_vps_list(cls.homepage + href, category)))
        vps_list = await asyncio.gather(*tasks)
        return list(itertools.chain(*vps_list))

    @classmethod
    async def get_datacenter_list(cls) -> list[DataCenter]:
        url = f"{cls.homepage}/knowledgebase/4/Test-IPv4-Addresses.html"
        session = cls._get_session()
        r = await session.get(url, timeout=cls.timeout)
        ips = r.html.find("p")[1].text.split("\n")
        datacenter_list = []
        for ip in ips:
            ip = ip.split("(")[0]
            location, ipv4 = ip.split(":")
            name, location = location.split(",")
            datacenter_list.append(
                DataCenter(
                    provider=cls.type,
                    name=name.strip(),
                    location=location.strip(),
                    ipv4=ipv4.strip(),
                )
            )
        return datacenter_list
