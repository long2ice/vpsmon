from vpsmon.providers.shockhosting import ShockHosting


async def test_get_vps_list():
    vps_list = await ShockHosting.get_vps_list()
    assert len(vps_list) > 0


async def test_get_datacenter_list():
    datacenters = await ShockHosting.get_datacenter_list()
    assert len(datacenters) > 0
