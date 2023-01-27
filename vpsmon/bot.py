from typing import Optional

from telegram import Bot, BotCommand, Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.exceptions import IntegrityError

from vpsmon.models import VPS, Subscriber
from vpsmon.settings import settings
from vpsmon.utils import get_provider

bot = Bot(token=settings.TG_BOT_TOKEN)
app = ApplicationBuilder().token(settings.TG_BOT_TOKEN).build()


async def check_vps_id(update: Update):
    if not update.message:
        return
    try:
        vps_id = update.message.text.split(" ")[1]
    except IndexError:
        await update.message.reply_text("请提供VPS ID")
        return
    if not vps_id.isdigit() and vps_id != "all":
        await update.message.reply_text("无效的VPS ID")
    if vps_id == "all":
        return vps_id
    vps = await VPS.exists(pk=vps_id)
    if not vps:
        await update.message.reply_text("无效的VPS ID")
        return
    return vps_id


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    vps_id = await check_vps_id(update)
    if not vps_id:
        return
    if vps_id == "all":
        await update.message.reply_text("无效的VPS ID")
        return
    chat_id = update.message.chat_id
    try:
        await Subscriber.create(chat_id=chat_id, vps_id=vps_id)
    except IntegrityError:
        await update.message.reply_text("已经订阅过该VPS")
        return
    await update.message.reply_text(
        text="订阅VPS成功",
    )


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    vps_id = await check_vps_id(update)
    if not vps_id:
        return
    chat_id = update.message.chat_id
    if vps_id == "all":
        count = await Subscriber.filter(chat_id=chat_id).delete()
        await update.message.reply_text(f"取消订阅所有VPS成功，共取消订阅{count}个VPS")
    else:
        await Subscriber.filter(chat_id=chat_id, vps_id=vps_id).delete()
        await update.message.reply_text(
            text="取消订阅VPS成功",
        )


subscribe_vps_template = "VPS ID: {id}  供应商: {provider}  名称: {name}  地址：<a href='{link}'>点击查看</a>"


async def list_vps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    subscribers = await Subscriber.filter(chat_id=chat_id).all()
    if not subscribers:
        await update.message.reply_text("还没有订阅任何VPS")
        return
    text = []
    for subscriber in subscribers:
        vps = await VPS.get(pk=subscriber.vps_id)  # type: ignore
        provider = get_provider(vps.provider)
        name = vps.name
        text.append(
            subscribe_vps_template.format(
                id=vps.pk,
                name=name,
                provider=provider.name,
                link=settings.vps_link(vps.pk),
            )
        )
    await update.message.reply_text(
        text="\n".join(text),
        parse_mode=ParseMode.HTML,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """/subscribe ID 订阅VPS\n/unsubscribe ID or all 取消订阅VPS\n/list 列出所有已订阅VPS\n/help 帮助
    """
    await update.message.reply_text(text)


async def start():
    await bot.set_my_commands(
        [
            BotCommand("subscribe", "订阅VPS"),
            BotCommand("unsubscribe", "取消订阅VPS"),
            BotCommand("list", "列出所有已订阅VPS"),
            BotCommand("help", "帮助"),
        ]
    )
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))
    app.add_handler(CommandHandler("list", list_vps))
    app.add_handler(CommandHandler("help", help_command))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()


async def stop():
    await app.updater.stop()
    await app.stop()
    await app.shutdown()


new_vps_template = """
{provider} VPS上新
名称：{name}
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
备注：{remarks}
购买地址：<a href='{link}'>点击购买</a>
"""

vps_model = pydantic_model_creator(
    VPS,
    exclude=("id", "created_at", "updated_at", "count", "speed", "bandwidth"),
    name="bot_vps",
)


async def send_new_vps(vps: VPS, chat_id: Optional[str] = None):
    async with bot:
        provider = get_provider(vps.provider)
        vps.provider = provider.name  # type: ignore
        vps.period = vps.period.title()  # type: ignore
        count = vps.count
        count_str = str(count)
        if count == -1:
            count_str = "无限制"
        elif count == 0:
            count_str = "暂时无货"
        speed = vps.speed
        speed_str = str(speed)
        if speed == -1:
            speed_str = "无限制"
        bandwidth = vps.bandwidth
        bandwidth_str = str(bandwidth)
        if bandwidth == -1:
            bandwidth_str = "无限制"
        vps.link = settings.vps_link(vps.pk)
        vps_dict = vps_model.from_orm(vps).dict()
        text = new_vps_template.format(
            count=count_str, speed=speed_str, bandwidth=bandwidth_str, **vps_dict
        )
        if chat_id:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=ParseMode.HTML,
            )
        else:
            await bot.send_message(
                chat_id=settings.TG_CHAT_ID,
                text=text,
                parse_mode=ParseMode.HTML,
            )
