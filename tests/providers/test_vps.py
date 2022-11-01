from vpsmon.providers.vps import VPSHosting


async def test_get_datacenter_list():
    datacenters = await VPSHosting.get_datacenter_list()
    assert len(datacenters) > 0


async def test_get_vps_list():
    vps_list = await VPSHosting.get_vps_list()
    assert len(vps_list) > 0
