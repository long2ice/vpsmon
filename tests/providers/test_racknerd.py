from vpsmon.providers.racknerd import RackNerd


async def test_get_datacenter_list():
    datacenters = await RackNerd.get_datacenter_list()
    assert len(datacenters) > 0


async def test_get_vps_list():
    vps_list = await RackNerd.get_vps_list()
    assert len(vps_list) > 0
