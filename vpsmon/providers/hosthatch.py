import asyncio
import itertools
import re
from typing import Optional

from loguru import logger

from vpsmon.enums import ProviderType
from vpsmon.models import VPS, DataCenter
from vpsmon.payment import BTC, BankTransfer, CreditCard, PayPal
from vpsmon.providers import Provider


class HostHatch(Provider):
    type = ProviderType.hosthatch
    icon = "https://hosthatch.com/img/favicon.png"
    name = "HostHatch"
    homepage = "https://hosthatch.com"
    payments = [
        PayPal,
        CreditCard,
        BTC,
        BankTransfer,
    ]
    datacenter_url = f"{homepage}/features#datacenters"
    aff = 2932
    aff_url = f"https://cloud.hosthatch.com/a/{2932}"

    @classmethod
    async def _get_vm(cls, url: str, category: str) -> list[VPS]:
        session = cls._get_session()
        r = await session.get(url, timeout=cls.timeout)
        vps_list = []
        for i, item in enumerate(r.html.find("product-presenter")):
            name = item.attrs["heading"]
            ps = item.find("p")
            cpu = ps[0].text.split(" ")[0]
            memory, memory_unit = ps[1].text.split(" ")[:2]
            if memory_unit == "GB":
                memory = float(memory) * 1024
            elif memory_unit == "MB":
                memory = float(memory)
            disk, disk_unit = ps[2].text.split(" ")[:2]
            dist_type = " ".join(ps[2].text.split(" ")[2:])
            if disk_unit == "GB":
                disk = float(disk)
            elif disk_unit == "TB":
                disk = float(disk) * 1024
            bandwidth, bandwidth_unit = ps[3].text.split(" ")[:2]
            if bandwidth_unit == "TB":
                bandwidth = float(bandwidth) * 1024
            elif bandwidth_unit == "GB":
                bandwidth = float(bandwidth)
            vps_list.append(
                VPS(
                    provider=cls.type,
                    category=category,
                    name=name,
                    cpu=cpu,
                    memory=memory,
                    disk=disk,
                    bandwidth=bandwidth,
                    dist_type=dist_type,
                    ipv4=1,
                )
            )
        return vps_list

    @classmethod
    async def get_vps_list(cls) -> list[VPS]:
        tasks = [
            asyncio.ensure_future(cls._get_vm(f"{cls.homepage}/ssd-vps", "Compute VM")),
            asyncio.ensure_future(cls._get_vm(f"{cls.homepage}/storage-vps", "Storage VM")),
        ]
        vps_list = await asyncio.gather(*tasks)
        return list(itertools.chain(*vps_list))

    @classmethod
    async def _get_datacenter(cls, location: str, name: str, href: str) -> Optional[DataCenter]:
        session = cls._get_session()
        try:
            r = await session.get(href)
        except Exception as e:
            logger.error(f"Failed to get datacenter {name} from {href}: {e}")
            return None
        ipv4 = re.findall(r"Test IPv4: (\d+\.\d+\.\d+\.\d+)", r.text)
        ipv6 = re.findall(r"Test IPv6: ([\da-f:]+)", r.text)
        return DataCenter(
            name=name,
            location=location,
            ipv4=ipv4,
            ipv6=ipv6,
        )

    @classmethod
    async def get_datacenter_list(cls) -> list[DataCenter]:
        session = cls._get_session()
        r = await session.get(cls.datacenter_url)
        table = r.html.find("table.datacenters", first=True)
        tasks = []
        for i, div in enumerate(table.find("tr")):
            if i == 0:
                continue
            tds = div.find("td")
            location = tds[0].text
            name = tds[1].text
            href = tds[2].find("a", first=True).attrs["href"]
            tasks.append(cls._get_datacenter(location, name, href))
        datacenter_list = await asyncio.gather(*tasks)
        return list(filter(lambda x: x is not None, datacenter_list))
