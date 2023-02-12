import asyncio
import itertools
import re

from vpsmon.enums import ProviderType
from vpsmon.models import VPS, DataCenter
from vpsmon.payment import BTC, ETH, AliPay, CreditCard, DebitCard, PayPal
from vpsmon.providers import Provider


class ShockHosting(Provider):
    type = ProviderType.shockhosting
    icon = "/provider/shockhosting.ico"
    name = "ShockHosting"
    homepage = "https://shockhosting.net"
    payments = [PayPal, AliPay, BTC, ETH, CreditCard, DebitCard]
    datacenter_url = "https://shockhosting.net/about#locations"
    aff = 994
    aff_url = f"https://shockhosting.net/portal/aff.php?aff={aff}"

    @classmethod
    async def _get_vps_list(cls, url: str, category: str):
        session = cls._get_session()
        r = await session.get(url, timeout=cls.timeout)
        vps_list = []
        text = r.text
        regex_name = r'\$\("#planname"\).text\("(.+)"\);'
        regex_cpu = r'\$\("#cpu"\).text\("(.+)"\);'
        regex_memory = r'\$\("#ram"\).text\("(.+)"\);'
        regex_disk = r'\$\("#ssd"\).text\("(.+)"\);'
        regex_bandwidth = r'\$\("#bw"\).text\("(.+)"\);'
        regex_price = r'\$\("#price"\).text\("(.+)"\);'
        links = r.html.find("a.sliderlink")
        hrefs = [link.attrs["href"] for link in links]
        names = re.findall(regex_name, text)
        cpus = re.findall(regex_cpu, text)
        memories = re.findall(regex_memory, text)
        disks = re.findall(regex_disk, text)
        bandwidths = re.findall(regex_bandwidth, text)
        prices = re.findall(regex_price, text)
        for name, cpu, memory, disk, bandwidth, price, href in zip(
            names, cpus, memories, disks, bandwidths, prices, hrefs
        ):
            price = float(price) + 0.99
            period = "month"
            cpu = cpu.split(" ")[0]
            memory, memory_unit = memory.split(" ")
            if memory_unit == "GB":
                memory = int(memory) * 1024
            else:
                memory = int(memory)
            disk, disk_unit = disk.split(" ")
            if disk_unit == "GB":
                disk = int(disk)
            else:
                disk = int(disk) * 1024
            bandwidth, bandwidth_unit = bandwidth.split(" ")
            if bandwidth_unit == "GB":
                bandwidth = int(bandwidth)
            else:
                bandwidth = int(bandwidth) * 1024
            vps_list.append(
                VPS(
                    name=name,
                    category=category,
                    cpu=cpu,
                    memory=memory,
                    disk=disk,
                    disk_type="SSD",
                    bandwidth=bandwidth,
                    price=price,
                    period=period,
                    ipv4=1,
                    speed=1024,
                    link=href + "&aff=" + str(cls.aff),
                )
            )
        return vps_list

    @classmethod
    async def get_vps_list(cls) -> list[VPS]:
        tasks = [
            asyncio.ensure_future(cls._get_vps_list(cls.homepage + "/vps", "Virtual Servers")),
        ]
        vps_list = await asyncio.gather(*tasks)
        return list(itertools.chain(*vps_list))

    @classmethod
    async def _get_data_center(cls, url: str) -> DataCenter:
        r = await cls._get_session().get(url, timeout=cls.timeout)
        ps = r.html.find(".well p")
        name = ps[0].find("span", first=True).text
        location = name.split(" ")[-1]
        ipv4 = ps[1].text.split(" ")[-1]
        ipv6 = ps[2].text.split(" ")[-1]
        return DataCenter(name=name, location=location, ipv4=ipv4, ipv6=ipv6)

    @classmethod
    async def get_datacenter_list(cls) -> list[DataCenter]:
        session = cls._get_session()
        r = await session.get(cls.datacenter_url)
        links = r.html.find(".colfirst > a")
        hrefs = [link.attrs["href"] for link in links]
        tasks = [asyncio.ensure_future(cls._get_data_center(href)) for href in hrefs]
        datacenters = await asyncio.gather(*tasks)
        return list(filter(None, datacenters))
