from vpsmon.enums import ProviderType
from vpsmon.models import VPS, DataCenter
from vpsmon.payment import AliPay, PayPal
from vpsmon.providers import Provider


class CloudCone(Provider):
    type = ProviderType.cloudcone
    icon = "/provider/cloudcone.png"
    name = "CloudCone"
    homepage = "https://cloudcone.com"
    payments = [PayPal, AliPay]
    aff = 8503
    aff_url = f"https://app.cloudcone.com/?ref={aff}"

    @classmethod
    async def get_vps_list(cls) -> list[VPS]:
        session = cls._get_session()
        vps_list = []
        r = await session.get(cls.homepage, timeout=cls.timeout)
        for div in r.html.find("div.pricing"):
            name = div.find("h5", first=True).text
            price = div.find("span.h1", first=True).text.replace("$", "")
            currency = "USD"
            period = "month"
            lis = div.find("ul li")
            cpu = lis[0].text.split(" ")[0]
            memory, memory_unit, _ = lis[1].text.split(" ")
            if memory_unit == "GB":
                memory = float(memory) * 1024
            elif memory_unit == "MB":
                memory = float(memory)
            disk, disk_unit, disk_type1, disk_type2 = lis[2].text.split(" ")
            if disk_unit == "GB":
                disk = float(disk)
            elif disk_unit == "TB":
                disk = float(disk) * 1024
            disk_type = disk_type1 + " " + disk_type2
            bandwidth, bandwidth_unit, _ = lis[3].text.split(" ")
            if bandwidth_unit == "TB":
                bandwidth = float(bandwidth) * 1024
            elif bandwidth_unit == "GB":
                bandwidth = float(bandwidth)
            ipv4 = lis[4].text.split(" ")[0]
            category = "Scalable Cloud Servers"
            link = div.find("a", first=True).attrs["href"] + f"&ref={cls.aff}"
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
                speed=1024,
            )
            vps_list.append(vps)
        return vps_list

    @classmethod
    async def get_datacenter_list(cls) -> list[DataCenter]:
        session = cls._get_session()
        r = await session.get("http://la.lg.cloudc.one")
        p_list = r.html.find("#information p")
        name, location = p_list[0].find("b", first=True).text.split(", ")
        ipv4 = p_list[1].text.split(" ")[-1]
        ipv6 = p_list[2].text.split(" ")[-1]
        return [
            DataCenter(
                provider=cls.type,
                name=name,
                location=location,
                ipv4=ipv4,
                ipv6=ipv6,
            )
        ]
