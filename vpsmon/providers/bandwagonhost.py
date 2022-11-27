import re

from vpsmon.enums import ProviderType
from vpsmon.models import VPS, DataCenter
from vpsmon.payment import AliPay, CreditCard, PayPal, UnionPay
from vpsmon.providers import Provider


class BandwagonHost(Provider):
    type = ProviderType.bandwagonhost
    icon = "/provider/bandwagonhost.png"
    name = "BandwagonHost"
    homepage = "https://bandwagonhost.com"
    payments = [PayPal, AliPay, UnionPay, CreditCard]
    aff = 69285
    aff_url = f"https://bandwagonhost.com/aff.php?aff={aff}"

    @classmethod
    async def get_vps_list(cls) -> list[VPS]:
        url = f"{cls.homepage}/vps-hosting.php"
        session = cls._get_session()
        r = await session.get(url)
        vps_list = []
        for div in r.html.find(".bronze"):
            name = div.find("h2", first=True).text
            lis = div.find("li")
            try:
                disk, disk_unit, disk_type = lis[0].text.split(" ")
            except ValueError:
                disk, disk_type = lis[0].text.split(" ")
                disk = re.findall(r"\d+", disk)[0]
                disk_unit = "GB"
            if disk_unit == "GB":
                disk = float(disk)
            elif disk_unit == "TB":
                disk = float(disk) * 1024
            memory, memory_unit = lis[1].text.split(" ")
            if memory_unit == "GB":
                memory = float(memory) * 1024
            bandwidth, bandwidth_unit = lis[2].text.split(" ")
            if bandwidth_unit == "TB":
                bandwidth = float(bandwidth) * 1024
            cpu = re.findall(r"\d+", lis[3].text)[0]
            speed, speed_unit = lis[4].text.split(" ")
            if speed_unit == "Gigabit":
                speed = float(speed) * 1024
            price, period = lis[9].text.split(" ")
            if period == "/mo":
                period = "month"
            elif period == "/yr":
                period = "year"
            price = re.findall(r"\d+", price)[0]
            a = div.find("a", first=True)
            pid = re.findall(r"pid=(\d+)", a.attrs["href"])[0]
            link = f"{cls.aff_url}&pid={pid}"
            vps = VPS(
                provider=cls.type,
                category="VPS Hosting",
                name=name,
                price=price,
                currency="USD",
                period=period,
                cpu=cpu,
                memory=memory,
                disk=disk,
                disk_type=disk_type,
                bandwidth=bandwidth,
                ipv4=1,
                link=link,
                speed=speed,
            )
            vps_list.append(vps)
        return vps_list

    @classmethod
    async def get_datacenter_list(cls) -> list[DataCenter]:
        session = cls._get_session()
        r = await session.get("https://bhw81.net/datacenter.html")
        table = r.html.find("table", first=True)
        datacenters = []
        for tr in table.find("tr"):
            tds = tr.find("td")
            if not tds:
                continue
            name = tds[0].text
            location = tds[1].text
            ipv4 = tds[2].text
            datacenter = DataCenter(
                name=name,
                location=location,
                ipv4=cls._check_ipv4(ipv4),
                provider=cls.type,
            )
            datacenters.append(datacenter)
        return datacenters
