import pytest

from vpsmon import bot
from vpsmon.enums import ProviderType
from vpsmon.models import VPS


@pytest.mark.skip
async def test_send_new_vps():
    vps = VPS(
        provider=ProviderType.racknerd,
        category="KVM VPS",
        name="KVM VPS 1",
        cpu=1,
        memory=1024,
        disk=20,
        disk_type="SSD",
        bandwidth=1000,
        speed=1000,
        ipv4=1,
        ipv6=0,
        price=2.99,
        currency="USD",
        period="month",
        count=1,
        link="https://www.racknerd.com/vps-hosting",
    )
    await bot.send_new_vps(vps)
