from vpsmon.providers.dmit import DMIT


async def test_get_datacenter_list():
    datacenters = await DMIT.get_datacenter_list()
    assert len(datacenters) > 0


async def test_get_vps_list():
    vps_list = await DMIT.get_vps_list()
    assert len(vps_list) > 0
