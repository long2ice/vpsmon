import re

from vpsmon.enums import ProviderType, VPSPeriod
from vpsmon.models import VPS, DataCenter
from vpsmon.payment import AliPay, BankTransfer, CreditCard, PayPal, Stripe
from vpsmon.providers import Provider


class DMIT(Provider):
    type = ProviderType.dmit
    icon = "https://www.dmit.io/favicon.ico"
    name = "Dmit"
    homepage = "https://www.dmit.io"
    payments = [PayPal, AliPay, BankTransfer, CreditCard, Stripe]
    datacenter_url = "https://walixz.com/dmit-speedtest.html"
    aff = 5324
    aff_url = f"{homepage}/aff.php?aff={aff}"

    @classmethod
    async def get_vps_list(cls) -> list[VPS]:
        url = f"{cls.homepage}/pages/pricing"
        session = cls._get_session()
        r = await session.get(url)
        vps_list = []
        table_options = r.html.find(".series")
        table_area = r.html.find(".table-area")
        for i, option in enumerate(table_options):
            area = table_area[i]
            category = option.text.strip().lstrip("- ")
            for tr in area.find("tr"):
                tds = tr.find("td")
                if not tds:
                    continue
                name = tr.find("th", first=True).text
                cpu = tds[0].text.split(" ")[0].strip("+")
                memory = tds[1].text.strip("+")
                if memory.endswith("GB"):
                    memory = float(memory.split("GB")[0].strip("+ ")) * 1024
                elif memory.endswith("MB"):
                    memory = float(memory.split("GB")[0].strip("+ "))
                try:
                    disk, disk_type = tds[2].text.split(" ")
                except ValueError:
                    disk_text = tds[2].text.split(" ")
                    disk = " ".join(disk_text[:2])
                    disk_type = disk_text[-1]

                if disk.endswith("GB"):
                    disk = float(disk.split("GB")[0].strip("+ "))
                elif disk.endswith("TB"):
                    disk = float(disk.split("TB")[0].strip("+ ")) * 1024
                bandwidth = tds[3].text
                if bandwidth.endswith("GB"):
                    bandwidth = float(bandwidth.split("GB")[0].strip("+ "))
                elif bandwidth.endswith("TB"):
                    bandwidth = float(bandwidth.split("TB")[0].strip("+ ")) * 1024
                elif bandwidth == "Unmetered":
                    bandwidth = -1
                ipv4, ipv6 = tds[4].text.split(" & ")
                ipv4 = ipv4.split(" ")[0]
                ipv6 = ipv6.split(" ")[0]
                try:
                    price, period = tds[7].text.split("/")
                    speed = tds[6].text.strip("+")
                    if speed.endswith("Gbps"):
                        speed = float(speed.split("Gbps")[0]) * 1024
                    elif speed.endswith("Mbps"):
                        speed = float(speed.split("Mbps")[0])
                except ValueError:
                    try:
                        price, period = tds[5].text.split("/")
                        speed = -1
                    except ValueError:
                        speed = tds[5].text
                        if speed.endswith("Gbps"):
                            speed = float(speed.split("Gbps")[0]) * 1024
                        elif speed.endswith("Mbps"):
                            speed = float(speed.split("Mbps")[0])
                        price, period = tds[6].text.split("/")

                if period == "Quarterly":
                    period = VPSPeriod.quarterly
                elif period == "Monthly":
                    period = VPSPeriod.month
                price = price.split(" ")[1]
                pid = re.findall(r"pid=(\d+)", tr.html)[0]
                link = f"{cls.aff_url}&pid={pid}"
                vps = VPS(
                    provider=cls.type,
                    category=category,
                    name=name,
                    price=price,
                    currency="USD",
                    period=period,
                    cpu=cpu,
                    memory=memory,
                    disk=disk,
                    disk_type=disk_type,
                    bandwidth=bandwidth,
                    ipv4=ipv4,
                    ipv6=ipv6,
                    link=link,
                    speed=speed,
                    count=-1,
                )
                vps_list.append(vps)
        return vps_list

    @classmethod
    async def get_datacenter_list(cls) -> list[DataCenter]:
        session = cls._get_session()
        r = await session.get(cls.datacenter_url)
        table = r.html.find("table", first=True)
        datacenters = []
        for tr in table.find("tr"):
            tds = tr.find("td")
            if not tds:
                continue
            location = tds[0].text
            name = tds[1].text
            ipv4 = tds[2].text
            datacenter = DataCenter(
                name=location + " " + name,
                location=location,
                ipv4=cls._check_ipv4(ipv4),
                provider=cls.type,
            )
            datacenters.append(datacenter)
        return datacenters
