import asyncio
import itertools
import re

from vpsmon.enums import ProviderType
from vpsmon.models import VPS, DataCenter
from vpsmon.payment import AliPay, PayPal, UnionPay
from vpsmon.providers import Provider


class LiCloud(Provider):
    type = ProviderType.licloud
    icon = "https://licloud.io/static/custom/img/favicon.png"
    name = "LiCloud"
    homepage = "https://licloud.io"
    aff = 304
    aff_url = f"https://my.licloud.io/aff.php?aff={aff}"
    payments = [PayPal, AliPay, UnionPay]
    datacenter_url = ""

    @classmethod
    async def get_vps_list(cls) -> list[VPS]:
        tasks = [
            asyncio.ensure_future(
                cls._get_vps_list(f"{cls.homepage}/product/vps.html")
            ),
            asyncio.ensure_future(
                cls._get_vps_list(f"{cls.homepage}/product/cloud.html")
            ),
        ]
        vps_list = await asyncio.gather(*tasks)
        return list(itertools.chain(*vps_list))

    @classmethod
    async def _get_vps_list(cls, url: str) -> list[VPS]:
        session = cls._get_session()
        vps_list = []
        r = await session.get(url)
        tables = r.html.find("table")
        h5 = r.html.find("h5.mb-1")
        h2 = r.html.find("h2")
        for i, table in enumerate(tables):
            trs = table.find("tr.vps-pricing-row")
            for tr in trs:
                tds = tr.find("td")
                cpu = re.findall(r"\d+", tds[0].text)[0]
                memory = re.findall(r"\d+", tds[1].text)[0]
                memory_unit = re.findall(r"[a-zA-Z]+", tds[1].text)[0]
                if memory_unit == "GB":
                    memory = float(memory) * 1024
                elif memory_unit == "MB":
                    memory = float(memory)
                disk = re.findall(r"\d+", tds[2].text)[0]
                disk_unit = re.findall(r"[a-zA-Z]+", tds[2].text)[0]
                if disk_unit == "GB":
                    disk = float(disk)
                elif disk_unit == "TB":
                    disk = float(disk) * 1024
                ip = tds[3].text.split(" ")[0]
                speed = re.findall(r"\d+", tds[4].text)[0]
                speed_unit = re.findall(r"[a-zA-Z]+", tds[4].text)[0]
                if speed_unit == "Gbps":
                    speed = float(speed) * 1024
                elif speed_unit == "Mbps":
                    speed = float(speed)
                bandwidth = re.findall(r"\d+", tds[5].text)[0]
                bandwidth_unit = re.findall(r"[a-zA-Z]+", tds[5].text)[0]
                if bandwidth_unit == "TB":
                    bandwidth = float(bandwidth) * 1024
                elif bandwidth_unit == "GB":
                    bandwidth = float(bandwidth)
                price = tds[6].find("span.rate", first=True).text
                price, period = price.split("/")
                price = float(price.split("$")[1])
                currency = "USD"
                if period == "每月":
                    period = "month"
                elif period == "每年":
                    period = "year"
                href = tds[7].find("a", first=True).attrs["href"]
                if href == "##":
                    count = 0
                    link = cls.aff_url
                else:
                    count = -1
                    pid = re.findall(r"pid=(\d+)", href)[0]
                    link = f"{cls.aff_url}&pid={pid}"
                vps = VPS(
                    provider=cls.type,
                    name=tds[0].text + " " + tds[1].text,
                    category=h5[i].text.split("(")[0] if h5 else h2[i].text,
                    cpu=cpu,
                    memory=memory,
                    disk=disk,
                    disk_type="Ceph存儲",
                    ipv4=ip,
                    speed=speed,
                    bandwidth=bandwidth,
                    price=price,
                    currency=currency,
                    period=period,
                    count=count,
                    link=link,
                )
                vps_list.append(vps)
        return vps_list

    @classmethod
    async def _get_datacenter(cls, url: str) -> DataCenter:
        session = cls._get_session()
        r = await session.get(url)
        p_list = r.html.find("#information p")
        name = p_list[0].find("span", first=True).text
        ipv4 = p_list[1].text.split(" ")[-1]
        return DataCenter(
            provider=cls.type,
            name=name,
            location="Hong Kong",
            ipv4=ipv4,
            ipv6=None,
        )

    @classmethod
    async def get_datacenter_list(cls) -> list[DataCenter]:
        datacenter_list = [
            await cls._get_datacenter("http://lg.hk-bgp.licloud.io"),
            await cls._get_datacenter("http://lg.hk-cn2.licloud.io"),
        ]
        return datacenter_list
