from aiogram import Bot, Dispatcher
import asyncio
from database.mongobase import admin_calleks
from calbacklar.buttonlarga import reminder_worker
# Routers
from habarlar.obunavasaqlashhabar import rt as obuansaq
from calbacklar.postga import rt as postli
from database.mongobase import rt as momngoga
from habarlar.nastroyka_uchun import rt as habarnastroy
from calbacklar.buttonlarga import rt as buttonlarga
from habarlar.pulkiritish import rt as pulga
from admin.Carta import rt as cartalar
from habarlar.salombotuchu import rt as salom_answer
from habarlar.Freehabarlari import rt as Freegade, monitor_all
from calbacklar.tilcallback import rt as tilcall
from kanal.Kanalumirga import rt as umrlik_router
from kanal.Kanalvaqt import rt as vaqt_kanal
from kanal.obunachili_kanal import rt as obuna_kanal
from kanal.maxfiy_kanal import rt as obuna_maxfiy
from kanal.ijtimoiytarmoqlar import rt as ijdimoiy_obuna
from kanal.ochirisahkanal import rt as ochir_obuna
from calbacklar.Yuklash_callback import rt as yulahganda
from Yuklash.conetntturi import rt as conetntga
from habarlar.nastroykapanel import rt as nastroykapane
from Yuklash.Yuklash_bu import rt as anime_yuk
from Yuklash.Shorts import rt as short
from admin.adminqosh import rt as admin_router


BOT_TOKEN = "8085300515:AAFVNBMejfY2T1vqXj8-D6INbfLBO1yxzXE"

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


routers = [
    umrlik_router,
    buttonlarga,
    habarnastroy,
    vaqt_kanal,
    obuna_maxfiy,
    admin_router,
    ijdimoiy_obuna,
    obuna_kanal,
    anime_yuk,
    ochir_obuna,
    Freegade,
    pulga,
    short,
    tilcall,
    cartalar,
    yulahganda,
    nastroykapane,
    obuansaq,
    postli,
    momngoga,
    conetntga,
    salom_answer
]

async def notify_admins_on_start(bot: Bot):

    admins = list(admin_calleks.find())

    bot_info = await bot.get_me()

    text = (
        f"🚀 <b>Bot ishga tushdi!</b>\n\n"
        f"🤖 <b>Nomi:</b> {bot_info.full_name}\n"
        f"📛 <b>Username:</b> @{bot_info.username}\n"
        f"🆔 <b>ID:</b> <code>{bot_info.id}</code>\n"
        f"🔗 <b>Link:</b> https://t.me/{bot_info.username}"
    )

    photos = await bot.get_user_profile_photos(bot_info.id)

    for admin in admins:
        try:
            if photos.total_count > 0:
                file_id = photos.photos[0][-1].file_id

                await bot.send_photo(
                    chat_id=admin["user_id"],
                    photo=file_id,
                    caption=text,
                    parse_mode="HTML"
                )
            else:
                await bot.send_message(
                    chat_id=admin["user_id"],
                    text=text,
                    parse_mode="HTML"
                )
        except:
            pass


async def main():

    for router in routers:
        dp.include_router(router)
    asyncio.create_task(monitor_all(bot))
    asyncio.create_task(reminder_worker(bot))
    await notify_admins_on_start(bot)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


