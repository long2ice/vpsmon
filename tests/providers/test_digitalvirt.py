from vpsmon.providers.digitalvirt import DigitalVirt


async def test_get_vps_list():
    vps_list = await DigitalVirt.get_vps_list()
    assert len(vps_list) > 0
