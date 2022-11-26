from vpsmon.providers.digitalvirt import DigitalVirt


async def test_get_vps_list():
    vps_list = await DigitalVirt.get_vps_list()
    assert len(vps_list) > 0


async def test_get_datacenter_list():
    datacenters = await DigitalVirt.get_datacenter_list()
    assert len(datacenters) > 0
