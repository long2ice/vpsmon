from telegram import Bot
from tortoise.contrib.pydantic import pydantic_model_creator

from vpsmon.models import VPS
from vpsmon.settings import settings
from vpsmon.utils import get_provider

bot = Bot(token=settings.TG_BOT_TOKEN)

vps_template = """
{provider} VPS上新
CPU：{cpu} 核
内存：{memory} MB
硬盘：{disk} GB
硬盘类型：{disk_type}
流量：{bandwidth} GB
带宽：{speed} Mbps
IPv4：{ipv4} 个
IPv6：{ipv6} 个
价格：{price} {currency} / {period}
数量：{count}
购买地址：{link}
"""

vps_model = pydantic_model_creator(
    VPS, exclude=("id", "created_at", "updated_at", "count", "speed")
)


async def send_new_vps(vps: VPS):
    async with bot:
        provider = get_provider(vps.provider)
        vps.provider = provider.name
        vps.period = vps.period.title()
        count = vps.count
        if count == -1:
            count = "无限制"
        elif count == 0:
            count = "暂时无货"
        speed = vps.speed
        if speed == -1:
            speed = "无限制"
        vps.link = settings.vps_link(vps.pk)
        vps_dict = vps_model.from_orm(vps).dict()
        await bot.send_message(
            settings.TG_CHAT_ID,
            vps_template.format(count=count, speed=speed, **vps_dict),
        )
