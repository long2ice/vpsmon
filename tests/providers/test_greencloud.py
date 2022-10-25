from vpsmon.providers.greencloud import GreenCloud


async def test_get_datacenter_list():
    datacenters = await GreenCloud.get_datacenter_list()
    assert len(datacenters) > 0


async def test_get_vps_list():
    vps_list = await GreenCloud.get_vps_list()
    assert len(vps_list) > 0


async def test_get_budget_vps():
    vps_list = await GreenCloud._get_budget_vps()
    assert len(vps_list) > 0
