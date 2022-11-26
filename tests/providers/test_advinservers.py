from vpsmon.providers.advinservers import AdvinServers


async def test_get_vps_list():
    vps_list = await AdvinServers.get_vps_list()
    assert len(vps_list) > 0
