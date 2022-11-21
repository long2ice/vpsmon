import asyncio
import itertools
import re

from vpsmon.enums import ProviderType
from vpsmon.models import VPS, DataCenter
from vpsmon.payment import (
    BTC,
    ETH,
    AliPay,
    BankTransfer,
    CreditCard,
    DebitCard,
    PayPal,
    PerfectMoney,
    UnionPay,
    WebMoneyZ,
)
from vpsmon.providers import Provider


class GreenCloud(Provider):
    type = ProviderType.greencloud
    icon = "https://greencloudvps.com/favicon.ico"
    name = "GreenCloud"
    homepage = "https://greencloudvps.com"
    payments = [
        PayPal,
        CreditCard,
        DebitCard,
        AliPay,
        UnionPay,
        WebMoneyZ,
        PerfectMoney,
        BTC,
        ETH,
        BankTransfer,
    ]
    datacenter_url = f"{homepage}/data-centers.php"
    aff = 4289
    aff_url = f"https://greencloudvps.com/billing/aff.php?aff={aff}"

    @classmethod
    async def _get_budget_vps(cls):
        url = f"{cls.homepage}/billing/store/budget-kvm-sale"
        session = cls._get_session()
        r = await session.get(url, timeout=cls.timeout)  # type: ignore
        vps_list = []
        products = r.html.find("div.product")
        for product in products:
            id_ = product.find(".product", first=True).attrs["id"]
            pid = id_.split("product")[1]
            name = product.find(f"#{id_}-name", first=True).text
            count = product.find("span.qty", first=True).text.split(" ")[0]
            memory_text = product.find(
                f"#{id_}-feature1 .feature-value", first=True
            ).text
            if memory_text.endswith("GB"):
                memory = float(memory_text.split("GB")[0]) * 1024
            else:
                memory = float(memory_text.split("MB")[0])
            disk_text = product.find(f"#{id_}-feature3 .feature-value", first=True).text
            disk_items = disk_text.split(" ")
            disk = disk_items[0]
            disk_type = " ".join(disk_items[1:])
            if disk.endswith("TB"):
                disk = int(float(disk.split("TB")[0]) * 1024)
            elif disk.endswith("GB"):
                disk = int(disk.split("GB")[0])
            cpu = product.find(
                f"#{id_}-feature4 .feature-value", first=True
            ).text.split(" ")[0]
            ipv4 = product.find(f"#{id_}-feature5 .feature-value", first=True).text
            ipv6 = product.find(
                f"#{id_}-feature6 .feature-value", first=True
            ).text.split("/")[1]
            ipv6 = 2 ** (128 - int(ipv6))
            bandwidth = product.find(f"#{id_}-feature7 .feature-value", first=True).text
            if bandwidth.endswith("TB"):
                bandwidth = int(float(bandwidth.split("TB")[0]) * 1024)
            elif bandwidth.endswith("GB"):
                bandwidth = int(bandwidth.split("GB")[0])
            speed = product.find(f"#{id_}-feature8 .feature-value", first=True).text
            if speed.endswith("Gbps"):
                speed = int(float(speed.split("Gbps")[0]) * 1024)
            elif speed.endswith("Mbps"):
                speed = int(speed.split("Mbps")[0])
            price, currency = product.find("span.price", first=True).text.split(" ")
            price = float(price[1:])
            product_price = product.find(".product-pricing", first=True).text
            period = "year"
            if "Triennially" in product_price:
                period = "triennium"
            remarks = product.find(f"#{id_}-feature10 .feature-value", first=True).text
            vps_list.append(
                VPS(
                    provider=cls.type,
                    category="Budget KVM Sale",
                    name=name,
                    link=f"{cls.aff_url}&pid={pid}",
                    price=price,
                    currency=currency,
                    count=count,
                    period=period,
                    bandwidth=bandwidth,
                    ipv4=ipv4,
                    ipv6=ipv6,
                    speed=speed,
                    cpu=cpu,
                    memory=memory,
                    disk=disk,
                    disk_type=disk_type,
                    remarks=remarks,
                )
            )
        return vps_list

    @classmethod
    async def _get_vps_list(cls, category: str, path: str):
        url = f"{cls.homepage}/{path}"
        session = cls._get_session()
        vps_list = []
        r = await session.get(url, timeout=cls.timeout)  # type: ignore
        tables = r.html.find(".tablesorter")
        for table in tables:
            for tr in table.find("tr"):
                tds = tr.find("td")
                if not tds:
                    continue
                name = tds[0].text
                disk, disk_type = tds[1].text.split(" ")
                if disk.endswith("GB"):
                    disk = int(disk.split("GB")[0])
                elif disk.endswith("TB"):
                    disk = int(disk.split("TB")[0]) * 1024
                cpu = tds[2].text.split(" ")[0]
                memory = tds[3].text
                if memory.endswith("GB"):
                    memory = float(memory.split("GB")[0]) * 1024
                elif memory.endswith("MB"):
                    memory = float(memory.split("MB")[0])
                bandwidth_text = tds[4].text
                if bandwidth_text == "Unmetered":
                    bandwidth = -1.0
                else:
                    bandwidth, bandwidth_unit = bandwidth_text.split(" ")
                    if bandwidth_unit == "TB":
                        bandwidth = float(bandwidth) * 1024
                    elif bandwidth_unit == "GB":
                        bandwidth = float(bandwidth)
                speed = tds[5].text.split(" ")[0]
                if speed.endswith("Gbps"):
                    speed = float(speed.split("Gbps")[0]) * 1024
                elif speed.endswith("Mbps"):
                    speed = float(speed.split("Mbps")[0])
                price, period = tds[8].text.split("/")
                if period == "mo":
                    period = "month"
                elif period == "yr":
                    period = "year"
                price = float(price.split("$")[1])
                currency = "USD"
                link = tds[9].find("a", first=True).attrs["href"]
                pid = None
                try:
                    pid = link.split("pid=")[1]
                except IndexError:
                    td_id = tds[9].attrs["id"]
                    if td_id:
                        modal = r.html.find(f"div#{td_id}", first=True)
                        pid = re.findall(r"pid=(\d+)", modal.html)
                        if pid:
                            pid = pid[0]
                vps = VPS(
                    provider=cls.type,
                    category=category,
                    name=name,
                    memory=memory,
                    cpu=cpu,
                    disk=disk,
                    disk_type=disk_type,
                    bandwidth=bandwidth,
                    speed=speed,
                    ipv4=1,
                    price=price,
                    currency=currency,
                    period=period,
                    link=cls.aff_url + f"&pid={pid}" if pid else link,
                )
                vps_list.append(vps)
        return vps_list

    @classmethod
    async def get_vps_list(cls) -> list[VPS]:
        tasks = [
            asyncio.ensure_future(
                cls._get_vps_list("Budget Windows VPS", "/budget-windows-vps.php")
            ),
            asyncio.ensure_future(
                cls._get_vps_list("SEO Optimized VPS", "/seo-optimized-vps.php")
            ),
            asyncio.ensure_future(
                cls._get_vps_list("Jarvee Optimized VPS", "/jarvee-optimized-vps.php")
            ),
            asyncio.ensure_future(
                cls._get_vps_list("High RAM VPS", "/high-ram-vps.php")
            ),
            asyncio.ensure_future(
                cls._get_vps_list("NVMe Windows VPS", "/nvme-windows-vps.php")
            ),
            asyncio.ensure_future(
                cls._get_vps_list("10Gbps Windows VPS", "/10gbps-windows-vps.php")
            ),
            asyncio.ensure_future(
                cls._get_vps_list("SEO Optimized VPS", "/seo-optimized-vps.php")
            ),
            asyncio.ensure_future(
                cls._get_vps_list("Managed Windows VPS", "/managed-windows-vps.php")
            ),
            asyncio.ensure_future(
                cls._get_vps_list("Ryzen KVM VPS", "/ryzen-kvm-vps.php")
            ),
            asyncio.ensure_future(
                cls._get_vps_list("NVMe KVM VPS", "/nvme-kvm-vps.php")
            ),
            asyncio.ensure_future(
                cls._get_vps_list("1Gbps SSD KVM VPS", "/1gbps-ssd-kvm-vps.php")
            ),
            asyncio.ensure_future(
                cls._get_vps_list("10Gbps KVM VPS", "/kvm-10gbps-vps.php")
            ),
            asyncio.ensure_future(
                cls._get_vps_list("Storage KVM VPS", "/storage-kvm-vps.php")
            ),
            asyncio.ensure_future(
                cls._get_vps_list("DE SSD KVM VPS", "/de-ssd-kvm-vps.php")
            ),
            asyncio.ensure_future(
                cls._get_vps_list("Hong Kong SSD KVM VPS", "/hong-kong-ssd-kvm-vps.php")
            ),
            asyncio.ensure_future(
                cls._get_vps_list("Singapore SSD KVM VPS", "/singapore-ssd-kvm-vps.php")
            ),
            asyncio.ensure_future(
                cls._get_vps_list("Vietnam SSD KVM VPS", "/vietnam-ssd-kvm-vps.php")
            ),
            asyncio.ensure_future(cls._get_budget_vps()),
        ]
        vps_list = await asyncio.gather(*tasks)
        return list(itertools.chain(*vps_list))

    @classmethod
    async def get_datacenter_list(cls) -> list[DataCenter]:
        session = cls._get_session()
        r = await session.get(cls.datacenter_url)  # type: ignore
        datacenter_list = []
        sections = r.html.find('div[data-element_type="column"] section')
        for section in sections:
            location = section.find("h4", first=True)
            if not location:
                continue
            location = location.text
            name = section.find("h2", first=True).text
            ps = section.find(".elementor-icon-box-description")
            ipv4 = ps[0].text.strip()
            try:
                ipv6 = ps[1].text.strip()
            except IndexError:
                ipv6 = None
            datacenter = DataCenter(
                name=name,
                location=location,
                ipv4=cls._check_ipv4(ipv4),
                ipv6=cls._check_ipv6(ipv6),
                provider=cls.type,
            )
            datacenter_list.append(datacenter)
        return datacenter_list
