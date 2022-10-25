from loguru import logger
from rearq import ReArq
from tortoise import Tortoise

from vpsmon.enums import ProviderType
from vpsmon.models import VPS, DataCenter
from vpsmon.settings import settings
from vpsmon.utils import get_provider, get_providers

rearq = ReArq(
    db_url=settings.DB_URL,
    redis_url=settings.REDIS_URL,
    keep_job_days=7,
    job_retry=0,
    job_timeout=60 * 30,
    expire=3 * 60,
    generate_schemas=True,
    trace_exception=settings.DEBUG,
)


@rearq.on_startup
async def startup():
    await Tortoise.init(
        db_url=settings.DB_URL,
        modules={"models": ["vpsmon.models"]},
    )


@rearq.on_shutdown
async def shutdown():
    await Tortoise.close_connections()


async def get_vps(type_: ProviderType):
    provider = get_provider(type_)
    vps_list = await provider.get_vps_list()
    await VPS.bulk_create(
        vps_list,
        on_conflict=["provider", "category", "name"],
        update_fields=[
            "cpu",
            "memory",
            "disk",
            "disk_type",
            "bandwidth",
            "link",
            "speed",
            "ipv4",
            "price",
            "currency",
            "period",
            "count",
        ],
    )
    return len(vps_list)


@rearq.task(cron="0 * * * *")
async def get_vps_list():
    providers = get_providers()
    for provider in providers:
        try:
            await get_vps(provider.type)
        except Exception as e:
            logger.error(f"Get VPS list from {provider.name} failed: {e}")


@rearq.task(cron="0 0 * * *")
async def get_datacenters():
    providers = get_providers()
    for provider in providers:
        await get_datacenter.delay(provider.type)


@rearq.task()
async def get_datacenter(type_: ProviderType):
    provider = get_provider(type_)
    datacenters = await provider.get_datacenter_list()
    await DataCenter.bulk_create(
        datacenters,
        on_conflict=["provider", "name"],
        update_fields=["ipv4", "ipv6", "location"],
    )
    return len(datacenters)
