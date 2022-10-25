import asyncio
import itertools
import re

import httpx
from requests_html import HTML

from vpsmon.enums import ProviderType
from vpsmon.models import VPS, DataCenter
from vpsmon.payment import WeChatPay
from vpsmon.providers import Provider


class DigitalVirt(Provider):
    type = ProviderType.digitalvirt
    icon = "https://digitalvirt.com/templates/BlueWhite/img/logo.png"
    name = "DigitalVirt"
    homepage = "https://digitalvirt.com"
    payments = [WeChatPay]
    aff = 120
    aff_url = f"https://digitalvirt.com/aff.php?aff={aff}"
    datacenter_url = aff_url

    @classmethod
    async def _get_vps_list(cls, url: str, category: str):
        vps_list = []
        async with httpx.AsyncClient(http2=True) as client:
            res = await client.get(url)
            html = HTML(html=res.text)
            for div in html.find("div.product-wrap-box"):
                name = div.find(".product-wrap-title", first=True).text
                price = (
                    div.find(".product-wrap-price .big", first=True).text.replace("¥", "").strip()
                )
                won = div.find(".product-wrap-price .won", first=True).text
                period = "month"
                if won == "年付":
                    period = "year"
                currency = "CNY"
                lis = div.find("ul li")
                cpu = lis[0].find("strong", first=True).text
                cpu = re.findall(r"\d+", cpu)[0]
                memory_text = lis[1].find("strong", first=True).text
                if memory_text.endswith("GB"):
                    memory = float(re.findall(r"\d+", memory_text)[0]) * 1024
                else:
                    memory = float(re.findall(r"\d+", memory_text)[0])
                try:
                    disk, disk_type = lis[2].find("strong", first=True).text.split(" ")
                except ValueError:
                    disk = lis[2].find("strong", first=True).text
                    disk_type = "SSD"
                if disk.endswith("G"):
                    disk = float(re.findall(r"\d+", disk)[0])
                elif disk.endswith("T"):
                    disk = float(re.findall(r"\d+", disk)[0]) * 1024
                speed_text = lis[3].find("strong", first=True).text
                if speed_text.endswith("Gbps"):
                    speed = float(re.findall(r"\d+", speed_text)[0]) * 1024
                else:
                    speed = float(re.findall(r"\d+", speed_text)[0])
                try:
                    bandwidth, _ = lis[4].find("strong", first=True).text.split("/")
                    if bandwidth.endswith("TB"):
                        bandwidth = float(re.findall(r"\d+", bandwidth)[0]) * 1024
                    else:
                        bandwidth = float(re.findall(r"\d+", bandwidth)[0])
                except (AttributeError, ValueError):
                    bandwidth = -1
                ipv4 = 1
                a = div.find("a", first=True)
                pid = re.findall(r"pid=(\d+)", a.attrs["href"])[0]
                link = f"{cls.aff_url}&pid={pid}"
                if a.text == "暂时售罄":
                    count = 0
                else:
                    count = -1
                vps = VPS(
                    provider=cls.type,
                    category=category,
                    name=name,
                    price=price,
                    currency=currency,
                    period=period,
                    cpu=cpu,
                    memory=memory,
                    disk=disk,
                    disk_type=disk_type,
                    bandwidth=bandwidth,
                    ipv4=ipv4,
                    link=link,
                    speed=speed,
                    count=count,
                )
                vps_list.append(vps)
        return vps_list

    @classmethod
    async def get_vps_list(cls) -> list[VPS]:
        tasks = [
            asyncio.ensure_future(cls._get_vps_list(f"{cls.homepage}/store/la-vps", "洛杉矶 9929")),
            asyncio.ensure_future(
                cls._get_vps_list(f"{cls.homepage}/store/la-vps-4837", "洛杉矶 4837")
            ),
            asyncio.ensure_future(cls._get_vps_list(f"{cls.homepage}/store/qn-vps", "洛杉矶 QN")),
            asyncio.ensure_future(cls._get_vps_list(f"{cls.homepage}/store/hk-cmi-vps", "香港 CMI")),
            asyncio.ensure_future(cls._get_vps_list(f"{cls.homepage}/store/hk-vps", "香港 CIA")),
            asyncio.ensure_future(cls._get_vps_list(f"{cls.homepage}/store/jp-vps-bbetc", "日本软银")),
        ]
        vps_list = await asyncio.gather(*tasks)
        return list(itertools.chain(*vps_list))

    @classmethod
    async def get_datacenter_list(cls) -> list[DataCenter]:
        return []
