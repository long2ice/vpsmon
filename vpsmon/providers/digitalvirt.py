import asyncio
import itertools
import json
import re
from typing import Optional
from urllib.parse import urlparse

import httpx
from requests_html import HTML
from websockets import connect  # type: ignore
from websockets.exceptions import InvalidStatusCode

from vpsmon.enums import ProviderType
from vpsmon.models import VPS, DataCenter
from vpsmon.payment import WeChatPay
from vpsmon.providers import Provider


class DigitalVirt(Provider):
    type = ProviderType.digitalvirt
    icon = "/provider/digitalvirt.webp"
    name = "DigitalVirt"
    homepage = "https://digitalvirt.com"
    payments = [WeChatPay]
    aff = 120
    aff_url = f"https://digitalvirt.com/aff.php?aff={aff}"

    @classmethod
    async def _get_vps_list(cls, path: str, category: str):
        vps_list = []
        url = f"{cls.homepage}/store{path}"
        async with httpx.AsyncClient(http2=True, timeout=cls.timeout) as client:
            res = await client.get(url)
            html = HTML(html=res.text)
            for div in html.find("div.product-wrap-box"):  # type: ignore
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
                    memory = float(memory_text.replace("GB", "").strip()) * 1024
                else:
                    memory = float(memory_text.replace("MB", "").strip())
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
                bandwidth = lis[4].find("strong", first=True).text
                try:
                    if "/" in bandwidth:
                        bandwidth, _ = bandwidth.split("/")
                    if bandwidth.endswith("T"):
                        bandwidth = float(re.findall(r"\d+", bandwidth)[0]) * 1024
                    elif bandwidth == "无限制":
                        bandwidth = -1
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
            asyncio.ensure_future(cls._get_vps_list("/la-vps", "洛杉矶 9929")),
            asyncio.ensure_future(cls._get_vps_list("/la-vps-4837", "洛杉矶 4837")),
            asyncio.ensure_future(cls._get_vps_list("/qn-vps", "洛杉矶 QN")),
            asyncio.ensure_future(cls._get_vps_list("/hk-cmi-vps", "香港 CMI")),
            asyncio.ensure_future(cls._get_vps_list("/la-vps-cn2gia", "洛杉矶 CN2 GIA")),
            asyncio.ensure_future(cls._get_vps_list("/jp-vps-bbetc", "日本软银")),
            asyncio.ensure_future(cls._get_vps_list("/sg-vps-bgp", "新加坡 BGP")),
            asyncio.ensure_future(cls._get_vps_list("/lightvm-9929", "洛杉矶轻量")),
            asyncio.ensure_future(cls._get_vps_list("/la-vps-cmin2", "洛杉矶 CMIN2")),
        ]
        vps_list = await asyncio.gather(*tasks)
        return list(itertools.chain(*vps_list))

    @classmethod
    async def _get_datacenter_list(cls, path: str, name: str) -> Optional[DataCenter]:
        url = f"{cls.homepage}/store{path}"
        async with httpx.AsyncClient(http2=True, timeout=cls.timeout) as client:
            res = await client.get(url)
            text = res.text
            datacenter_urls = re.findall(r"LookingGlass: (http://.+)</p>", text)
            if not datacenter_urls:
                return None
            datacenter_url = datacenter_urls[0]
            netloc = urlparse(datacenter_url).netloc
            ws_url = f"ws://{netloc}/ws"
            try:
                async with connect(ws_url) as websocket:
                    data = await websocket.recv()
                    data = data.split("|")[1]
                    data = json.loads(data)
                    public_ipv4 = data["public_ipv4"]
                    public_ipv6 = data["public_ipv6"] or ""
                    location = data["location"]
                    datacenter = DataCenter(
                        provider=cls.type,
                        name=name,
                        ipv4=public_ipv4,
                        ipv6=public_ipv6,
                        location=location,
                    )
                    return datacenter
            except InvalidStatusCode:
                return None

    @classmethod
    async def get_datacenter_list(cls) -> list[DataCenter]:
        tasks = [
            asyncio.ensure_future(cls._get_datacenter_list("/la-vps", "洛杉矶 9929")),
            asyncio.ensure_future(cls._get_datacenter_list("/la-vps-4837", "洛杉矶 4837")),
            asyncio.ensure_future(cls._get_datacenter_list("/qn-vps", "洛杉矶 QN")),
            asyncio.ensure_future(cls._get_datacenter_list("/hk-cmi-vps", "香港 CMI")),
            asyncio.ensure_future(cls._get_datacenter_list("/la-vps-cn2gia", "洛杉矶 CN2 GIA")),
            asyncio.ensure_future(cls._get_datacenter_list("/jp-vps-bbetc", "日本软银")),
        ]
        datacenter_list = await asyncio.gather(*tasks)
        return list(filter(None, datacenter_list))
