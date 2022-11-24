from vpsmon.providers.hosthatch import HostHatch


async def test_get_datacenter_list():
    datacenters = await HostHatch.get_datacenter_list()
    print(datacenters)
    assert len(datacenters) > 0


async def test_get_vps_list():
    vps_list = await HostHatch.get_vps_list()
    assert len(vps_list) > 0
