from vpsmon.providers.advinservers import AdvinServers


async def test_get_vps_list():
    vps_list = await AdvinServers.get_vps_list()
    assert len(vps_list) > 0


async def test_get_datacenter_list():
    datacenters = await AdvinServers.get_datacenter_list()
    assert len(datacenters) > 0
