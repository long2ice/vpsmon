from loguru import logger
from rearq import ReArq
from tortoise import Tortoise

from vpsmon.bot import send_new_vps
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


@rearq.task()
async def get_vps(type_: ProviderType):
    provider = get_provider(type_)
    created_count = 0
    updated_count = 0
    for vps in await provider.get_vps_list():
        defaults = {
            "cpu": vps.cpu,
            "memory": vps.memory,
            "disk": vps.disk,
            "disk_type": vps.disk_type,
            "bandwidth": vps.bandwidth,
            "ipv4": vps.ipv4,
            "ipv6": vps.ipv6,
            "price": vps.price,
            "currency": vps.currency,
            "period": vps.period,
            "link": vps.link,
            "count": vps.count,
            "speed": vps.speed,
        }
        instance = await VPS.get_or_none(
            provider=type_,
            name=vps.name,
            category=vps.category,
        )
        notify = False
        if instance:
            updated_count += 1
            if instance.count == 0 and vps.count > 0:
                notify = True
            await instance.update_from_dict(defaults).save()
        else:
            instance = await VPS.create(
                provider=type_,
                name=vps.name,
                category=vps.category,
                **defaults,
            )
            notify = True
            created_count += 1
        if not settings.DEBUG and notify:
            try:
                await send_new_vps(instance)
            except Exception as e:
                logger.exception(e)

    return {"created_count": created_count, "updated_count": updated_count}


@rearq.task(cron="0 * * * *")
async def get_vps_list():
    providers = get_providers()
    for provider in providers:
        await get_vps.delay(provider.type)


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
