from vpsmon.providers.bandwagonhost import BandwagonHost


async def test_get_datacenter_list():
    datacenters = await BandwagonHost.get_datacenter_list()
    assert len(datacenters) > 0


async def test_get_vps_list():
    vps_list = await BandwagonHost.get_vps_list()
    assert len(vps_list) > 0
