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
带宽：{bandwidth} Mbps
速率：{speed} Mbps
IPv4：{ipv4} 个
IPv6：{ipv6} 个
价格：{price} {currency} / {period}
数量：{count}
购买地址：{link}
"""

vps_model = pydantic_model_creator(VPS, exclude=("id", "created_at", "updated_at"))


async def send_new_vps(vps: VPS):
    async with bot:
        provider = get_provider(vps.provider)
        vps.provider = provider.name
        vps_dict = vps_model.from_orm(vps).dict()
        await bot.send_message(
            settings.TG_CHAT_ID,
            vps_template.format(**vps_dict),
        )