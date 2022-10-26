from vpsmon.providers.vultr import Vultr


async def test_get_datacenter_list():
    datacenters = await Vultr.get_datacenter_list()
    assert len(datacenters) > 0


async def test_get_vps_list():
    vps_list = await Vultr.get_vps_list()
    assert len(vps_list) > 0
