from vpsmon.providers.licloud import LiCloud


async def test_get_datacenter_list():
    datacenters = await LiCloud.get_datacenter_list()
    assert len(datacenters) > 0


async def test_get_vps_list():
    vps_list = await LiCloud.get_vps_list()
    assert len(vps_list) > 0
