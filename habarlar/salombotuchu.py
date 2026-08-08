from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from Inlinebutton import uzb_kb
from database.mongobase import (
    keyboard_collection,
    user_collection,
    korishlar_collection,
    anime_collection,
    qsmi_collection,
    Filim_collection
)
import html
rt = Router()


@rt.message(CommandStart())
async def start_answer(message: Message, state: FSMContext):

    bot = message.bot
    user_id = message.from_user.id

    user = user_collection.find_one({"user": user_id})

    # agar bazada bo'lmasa saqlaydi
    if user is None:
        user_collection.insert_one({
            "user": user_id,
            "balance": 0,
            "referal": 0,
            "last_button_press": None
        })

    if message.text and len(message.text.split()) > 1:

        secret_code = message.text.split()[1]

        # ANIME
        if secret_code.startswith("anime_"):
            code = secret_code.split("_")[1]

            # Anime va qismni olish
            anime = anime_collection.find_one({"code": code})
            qsimlar = list(qsmi_collection.find({"code": code}))  # barcha qismlar
            total_qsims = len(qsimlar)

            if not anime:
                await message.answer("*Bu start bilan anime topilmadi*", parse_mode="Markdown")
                return

            # Foydalanuvchi allaqachon ko‘rganini tekshirish
            exists = korishlar_collection.find_one({"user_id": user_id, "code": code})
            if not exists:
                korishlar_collection.insert_one({
                    "user_id": user_id,
                    "code": code,
                    "video_name": anime['nomi']
                })

            # Korishlar sonini yangilash
            korish = korishlar_collection.count_documents({"code": code})

            # Inline tugma
            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Yuklash♻", callback_data=f"nomi_{anime['code']}")]
                ]
            )

            # Caption tayyorlash
            caption = (
                f"📋*Nomi*: {anime['nomi']}\n"
                f"🎞*Qismi*: 1/{total_qsims}\n"
                f"🔣*Code*: {anime['code']}\n"
                f"🔠*Tili*: {anime['tili']}\n"
                f"🕑*Yili*: {anime['yili']}\n"
                f"*👁‍Korishlar*: {korish}"
            )

            # Foto yuborish
            await bot.send_photo(
                message.chat.id,
                photo=anime["photo"],
                caption=caption,
                parse_mode="Markdown",
                reply_markup=kb
            )

            # Foydalanuvchini bazaga qo‘shish, agar yo‘q bo‘lsa
            if not user_collection.find_one({"user": user_id}):
                user_collection.insert_one({
                    "user": user_id,
                    "balance": 0,
                    "referal": 0,
                    "last_button_press": None
                })

            # Kommentariya yuborish
            kommentar = keyboard_collection.find_one({"code": anime["code"]})
            if kommentar:
                await bot.send_message(
                    message.chat.id,
                    f"<b>Komentariya</b>\n{kommentar['komment']}\n<b>yozdi</b> {kommentar['mention']}",
                    parse_mode="HTML"
                )
            else:
                await message.answer("koment topilmadi🤔")

            # State update (agar FSM ishlatilsa)
            await state.update_data(shucode=anime["code"])

        # REFERAL
        elif secret_code.startswith("giwey_"):

            # Foydalanuvchi allaqachon bazada bormi tekshiradi
            existing_user = user_collection.find_one({"user": user_id})

            if existing_user:
                # Agar foydalanuvchi avvaldan bor bo‘lsa
                await message.answer(
                    "Kechirasiz, siz referal bo'la olmaysiz, avval botga tashrif buyurgansiz 😥😣"
                )

            else:
                # Referent ID ni olish
                referent_id = int(secret_code.split("_")[1])

                # Yangi foydalanuvchini bazaga qo‘shish va bonus berish
                user_collection.insert_one({
                    "user": user_id,
                    "balance": 50,  # yangi foydalanuvchi uchun bonus
                    "referal": 0,
                    "last_button_press": None
                })

                # Refer qilgan foydalanuvchiga bonus qo‘shish
                user_collection.update_one(
                    {"user": referent_id},
                    {
                        "$inc": {
                            "balance": 100,  # referent bonus
                            "referal": 1  # referal sonini oshirish
                        }
                    }
                )

                # Xabarlar yuborish
                await message.bot.send_message(
                    message.chat.id,
                    "Sizning referal silkangiz orqali botga foydalanuvchi tashrif buyurdi va 100 som hisobingizga o'tkazildi, shunday davom eting 🙃"
                )

                await message.answer(
                    "*Tabriklaymiz 🧨! Siz botga referal silka orqali kirdingiz va 50 som mukofot oldingiz*",
                    parse_mode="Markdown"
                )

        # FILM
        elif secret_code.startswith("filim_"):

            code = secret_code.split("_")[1]

            anime = anime_collection.find_one({"code": code})
            film = Filim_collection.find_one({"code": code})

            if anime and film:

                korish = korishlar_collection.count_documents({"code": code})

                caption = (
                    f"📋*Nomi*: {anime['nomi']}\n"
                    f"🎞*Qismi*: {anime['qismi']}\n"
                    f"🔣*Code*{anime['code']}\n"
                    f" 🔠*Tili*{anime['tili']}\n"
                    f" 🕑*Yili*{anime['yili']}\n"
                    f" 👁‍Korishlar{korish}"
                )

                await bot.send_video(message.chat.id, film["url"], caption=caption)

            else:
                await message.answer("bu start uchun anime mavjud emas yoki start eskirgan bolishi mumkin")

        # POST
        elif secret_code.startswith("post_"):

            parts = secret_code.split("_", 2)

            if len(parts) < 3:
                return await message.answer("❌ Noto‘g‘ri start link!")

            code = parts[1]
            qsim = parts[2]
            print(code)
            print(qsim)

            anime = anime_collection.find_one({"code": code})
            qsimli = qsmi_collection.find_one({"code": code, "qsimi": int(qsim)})

            if anime and qsimli:

                korish = korishlar_collection.count_documents({"code": code})

                caption = (
                    f"📋 <b>Nomi:</b> {html.escape(str(anime.get('nomi', '')))}\n"
                    f"🎞 <b>Qismi:</b> {html.escape(str(qsim))}\n"
                    f"🔣 <b>Code:</b> {html.escape(str(anime.get('code', '')))}\n"
                    f"🔠 <b>Tili:</b> {html.escape(str(anime.get('tili', '')))}\n"
                    f"🕑 <b>Yili:</b> {html.escape(str(anime.get('yili', '')))}\n"
                    f"👁 <b>Ko‘rishlar:</b> {korish}"
                )

                await bot.send_video(
                    chat_id=message.chat.id,
                    video=qsimli["url"],
                    caption=caption,
                    parse_mode="HTML"
                )

            else:
                await message.answer("❌ Anime topilmadi yoki link eskirgan")
    else:

        await message.answer(
            f"<b>Xush kelibsiz! {message.from_user.mention_html()}😎😘 Siz bu bot orqali hohlagan animeyingizni topishingiz✨ mumkin. Tugmalardan birini tanlang📂</b>",
            parse_mode="HTML",
            reply_markup=uzb_kb
        )

@rt.message(F.text & ~F.text.startswith("/"))
async def search_anime_by_code(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    text = message.text.strip()

    # Agarmatn raqam bo'lmasa (harf yuborilsa)
    if not text.isdigit():
        await message.answer(
            "⚠️ <b>Iltimos, harf yoki boshqa narsa yubormang! Anime qidirish uchun faqat kodni (raqamni) kiriting yoki tugmalardan foydalaning.</b>",
            parse_mode="HTML"
        )
        return

    # Bazadan kod bo'yicha animeni qidirish
    code = text
    anime = anime_collection.find_one({"code": code})

    if not anime:
        await message.answer("❌ <b>Bunday kodli anime topilmadi!</b> Qaytadan tekshirib ko'ring.", parse_mode="HTML")
        return

    qsimlar = list(qsmi_collection.find({"code": code}))
    total_qsims = len(qsimlar)

    # Ko'rishlar sonini olish
    exists = korishlar_collection.find_one({"user_id": user_id, "code": code})
    if not exists:
        korishlar_collection.insert_one({
            "user_id": user_id,
            "code": code,
            "video_name": anime['nomi']
        })

    korish = korishlar_collection.count_documents({"code": code})

    # Inline tugma (yuklab olish uchun)
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Yuklash♻", callback_data=f"nomi_{anime['code']}")]
        ]
    )

    caption = (
        f"📋*Nomi*: {anime['nomi']}\n"
        f"🎞*Qismi*: 1/{total_qsims}\n"
        f"🔣*Code*: {anime['code']}\n"
        f"🔠*Tili*: {anime['tili']}\n"
        f"🕑*Yili*: {anime['yili']}\n"
        f"*👁‍Korishlar*: {korish}"
    )

    # Rasmini yuborish
    await bot.send_photo(
        message.chat.id,
        photo=anime["photo"],
        caption=caption,
        parse_mode="Markdown",
        reply_markup=kb
    )

    # Kommentariyani tekshirib yuborish
    kommentar = keyboard_collection.find_one({"code": anime["code"]})
    if kommentar:
        await bot.send_message(
            message.chat.id,
            f"<b>Komentariya</b>\n{kommentar['komment']}\n<b>yozdi</b> {kommentar['mention']}",
            parse_mode="HTML"
        )

    # State update
    await state.update_data(shucode=anime["code"])