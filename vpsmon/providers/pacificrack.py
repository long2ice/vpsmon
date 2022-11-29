from vpsmon.enums import ProviderType
from vpsmon.models import VPS, DataCenter
from vpsmon.payment import AliPay, PayPal, UnionPay, WeChatPay
from vpsmon.providers import Provider


class Pacificrack(Provider):
    type = ProviderType.pacificrack
    icon = "/provider/pacificrack.webp"
    name = "Pacificrack"
    homepage = "https://pacificrack.com"
    aff = 3951
    aff_url = f"https://pacificrack.com/portal/aff.php?aff={aff}"
    payments = [PayPal, AliPay, UnionPay, WeChatPay]
    enable = False

    @classmethod
    async def get_vps_list(cls) -> list[VPS]:
        url = f"{cls.homepage}/ssd-vps.html"
        session = cls._get_session()
        vps_list = []
        r = await session.get(url, timeout=cls.timeout)  # type: ignore
        boxes = r.html.find("div.ssdvps-plan-box")
        for box in boxes:
            name = box.find("span.ssdvps-plan-span", first=True).text
            price = box.find("h3", first=True).text
            price = float(price.split("$")[1])
            currency = "USD"
            period = box.find("p", first=True).text
            if period == "Monthly":
                period = "month"
            elif period == "Yearly":
                period = "year"
            lis = box.find("ul li")
            cpu = lis[0].text.lstrip("CPU").strip()
            memory, memory_unit = lis[1].text.lstrip("RAM").split(" ")
            if memory_unit == "GB":
                memory = float(memory) * 1024
            elif memory_unit == "MB":
                memory = float(memory)
            disk, disk_unit = lis[2].text.lstrip("SSD").split(" ")
            if disk_unit == "GB":
                disk = float(disk)
            elif disk_unit == "TB":
                disk = float(disk) * 1024
            speed, speed_unit = lis[3].text.lstrip("Port Speed").split(" ")
            if speed_unit == "Gbps":
                speed = float(speed) * 1024
            elif speed_unit == "Mbps":
                speed = float(speed)
            bandwidth, bandwidth_unit = lis[4].text.lstrip("Bandwidth").split(" ")
            if bandwidth_unit == "TB":
                bandwidth = float(bandwidth) * 1024
            elif bandwidth_unit == "GB":
                bandwidth = float(bandwidth)
            ipv4 = lis[5].text.lstrip("IPv4").split(" ")[0]
            link = box.find("a", first=True).attrs["href"]
            vps = VPS(
                provider=cls.type,
                category="SSD VPS",
                name=name,
                cpu=cpu,
                memory=memory,
                disk=disk,
                disk_type=r.html.find(".plan-comparison-box", first=True).find("li")[2].text,
                speed=speed,
                bandwidth=bandwidth,
                ipv4=ipv4,
                price=price,
                currency=currency,
                period=period,
                link=link,
            )
            vps_list.append(vps)
        return vps_list

    @classmethod
    async def get_datacenter_list(cls) -> list[DataCenter]:
        session = cls._get_session()
        r = await session.get("https://lg.pacificrack.com")
        p_list = r.html.find("#information p")
        name = p_list[0].find("b", first=True).text
        ipv4 = p_list[1].text.split(" ")[-1]
        return [
            DataCenter(
                provider=cls.type,
                name=name,
                location="USA",
                ipv4=ipv4,
                ipv6=None,
            )
        ]
