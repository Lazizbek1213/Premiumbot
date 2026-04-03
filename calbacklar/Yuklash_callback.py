from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from database.mongobase import anime_collection, qsmi_collection, korishlar_collection, saved_collection, subscribers_collection, TrueFalse_Y
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
import Statelar
import random
from Inlinebutton import generate_inline_buttons, izlashuchun


rt = Router()


# Anime yuklash (1-qism)
async def yuklash_anime(call: CallbackQuery, bot: Bot):
    data = call.data.split("_")

    # Code tekshirish
    try:
        code = data[1]
    except (IndexError, ValueError):
        await call.message.answer("Noto‘g‘ri kod!")
        return

    users = list(qsmi_collection.find({"code": code}))
    qsim = qsmi_collection.find_one({"code": code, "qsimi": 1})

    if not qsim:
        await call.message.answer("Bu qism topilmadi!")
        return

    inline = generate_inline_buttons(users, start_index=0)

    try:
        anime = anime_collection.find_one({"code": qsim.get("code")})

        await bot.send_video(
            chat_id=call.message.chat.id,
            video=qsim["url"],
            caption=f"""🏷Anime nomi: {anime.get('nomi')}
📽Qismlar soni: {anime.get('qismi')}
🖋Janri: {anime.get('janr', '-')}
💬Tili: {anime.get('tili', '-')}
🕑Yili: {anime.get('yili', '-')}

🎬 Qism: {qsim.get('qsimi')}""",
            reply_markup=inline
        )
    except Exception as e:
        await call.message.answer(f"Video yuborishda xatolik: {e}")


async def send_anime(call: CallbackQuery, bot: Bot):
    data = call.data.split("_")
    code = data[1]
    qism = int(data[2])

    qsmi = qsmi_collection.find_one({"code": code, "qsimi": qism})
    if not qsmi:
        await call.message.answer("❌ Bu qism topilmadi")
        return

    # anime info
    anime = anime_collection.find_one({"code": code})
    if not anime:
        await call.message.answer("❌ Anime topilmadi")
        return

    # jami qismlar soni
    total_qsims = qsmi_collection.count_documents({"code": code})

    # Inline tugmalar
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📌 Obuna", callback_data=f"subscribe_{code}_{anime['nomi']}"),
                InlineKeyboardButton(text="💾 Saqlash", callback_data=f"save_{code}_{anime['nomi']}")
            ],
            [
                InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"delete_{code}_{qism}")
            ]
        ]
    )

    # captionni yangilash
    caption = (
        f"🏷Anime nomi: {anime.get('nomi')}\n"
        f"📽Qism: {qism}/{total_qsims}\n"
        f"🖋Janri: {anime.get('janr', '-')}\n"
        f"💬Til: {anime.get('tili', '-')}\n"
        f"🕑Yili: {anime.get('yili', '-')}"
    )

    # protect_content
    content = TrueFalse_Y.find_one()
    protect = content.get("enabled", True) if content else True

    await bot.send_video(
        chat_id=call.message.chat.id,
        video=qsmi["url"],
        caption=caption,
        parse_mode="Markdown",
        reply_markup=kb,
        protect_content=protect  # ✅ shu yerda ishlatish kerak
    )


# Next qism
async def next_qism(call: CallbackQuery, bot: Bot):

    data = call.data.split("_")

    start_index = int(data[1])
    code = int(data[2])
    qsim_number = int(data[3])

    users = list(qsmi_collection.find({"code": code}))

    qsim = qsmi_collection.find_one({
        "code": code,
        "qsimi": qsim_number
    })

    inline = generate_inline_buttons(users, start_index=start_index)

    await bot.delete_message(call.message.chat.id, call.message.message_id)

    await bot.send_video(
        chat_id=call.message.chat.id,
        video=qsim["url"],
        reply_markup=inline
    )


# Prev qism
async def prev_qism(call: CallbackQuery, bot: Bot):

    data = call.data.split("_")

    start_index = int(data[1])
    code = int(data[2])
    qsim_number = int(data[3])

    users = list(qsmi_collection.find({"code": code}))

    qsim = qsmi_collection.find_one({
        "code": code,
        "qsimi": qsim_number
    })

    inline = generate_inline_buttons(users, start_index=start_index)

    await bot.delete_message(call.message.chat.id, call.message.message_id)

    await bot.send_video(
        chat_id=call.message.chat.id,
        video=qsim["url"],
        reply_markup=inline
    )


# NOMI BOYICHA IZLASH
async def nomi_izlash(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Anime nomini yozing 🔍")
    await state.set_state(Statelar.nomi1.nomi)


# JANR BOYICHA
async def janr_izlash(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Janr yozing (#action kabi) 🎭")
    await state.set_state(Statelar.janrlar.janr)


# CODE BOYICHA
async def code_izlash(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Anime codini yozing 🗓")
    await state.set_state(Statelar.code1.code)


# YIL BOYICHA
async def yil_izlash(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Anime yilini yozing ⏲")
    await state.set_state(Statelar.Yili.yili)


# RANDOM ANIME
async def random_anime(call: CallbackQuery):

    animes = list(anime_collection.find())

    if not animes:
        await call.message.answer("Anime topilmadi")
        return

    anime = random.choice(animes)

    korish = korishlar_collection.count_documents({"code": anime["code"]})

    caption = f"""
🎥 Nomi: {anime['nomi']}
🎞 Qismlar: {anime['qismi']}
🎭 Janr: {anime['janr']}
🔢 Code: {anime['code']}
🕑 Yil: {anime['yili']}
👁 Korishlar: {korish}
"""

    await call.message.answer_photo(
        photo=anime["photo"],
        caption=caption
    )


async def kop_korilgan(call: CallbackQuery):

    pipeline = [
        {
            "$group": {
                "_id": "$code",
                "views": {"$sum": 1}
            }
        },
        {
            "$sort": {"views": -1}
        },
        {
            "$limit": 10
        }
    ]

    results = list(korishlar_collection.aggregate(pipeline))

    if not results:
        await call.message.answer("❌ Hali ko‘rishlar yo‘q")
        return

    text = "🔥 Eng ko‘p ko‘rilgan animelar:\n\n"

    for i, item in enumerate(results):
        code = item["_id"]
        views = item["views"]

        text += f"{i+1}. 🎬 Code: {code} — 👁 {views} ta\n"

    await call.message.answer(text)


# TOP ANIME
async def top_anime(call: CallbackQuery):

    animes = list(anime_collection.find().limit(10))

    text = "📊 Top animelar:\n\n"

    for i, anime in enumerate(animes):
        text += f"{i+1}. {anime['nomi']}\n"

    await call.message.answer(text)

search_cache = {}

# 🔹 UNIVERSAL BUTTON GENERATOR
def generate_search_buttons(results, start=0, limit=6):
    keyboard = []

    end = start + limit
    sliced = results[start:end]

    # Anime buttonlar
    for anime in sliced:
        keyboard.append([
            InlineKeyboardButton(
                text=f"🎬 {anime['nomi']}",
                callback_data=f"nomi_{anime['code']}"
            )
        ])

    # Pagination tugmalar
    nav = []

    if start > 0:
        nav.append(
            InlineKeyboardButton(text="◀ Oldingi", callback_data=f"page_{start - limit}")
        )

    if end < len(results):
        nav.append(
            InlineKeyboardButton(text="Keyingi ▶", callback_data=f"page_{start + limit}")
        )

    if nav:
        keyboard.append(nav)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# 🔎 NOMI BOYICHA
async def nomi_qidir(message: Message, state: FSMContext):
    text = message.text.strip()

    results = list(anime_collection.find({
        "nomi": {"$regex": text, "$options": "i"}
    }))

    if not results:
        await message.answer("❌ Anime topilmadi")
        return

    search_cache[message.from_user.id] = results

    kb = generate_search_buttons(results)

    await message.answer(
        f"🔍 Topildi: {len(results)} ta\nKeraklisini tanlang 👇",
        reply_markup=kb
    )

    await state.clear()


# 🎭 JANR BOYICHA
async def janr_qidir(message: Message, state: FSMContext):
    text = message.text.strip()

    results = list(anime_collection.find({
        "janr": {"$regex": text, "$options": "i"}
    }))

    if not results:
        await message.answer("❌ Janr bo‘yicha topilmadi")
        return

    search_cache[message.from_user.id] = results

    kb = generate_search_buttons(results)

    await message.answer(
        f"🎭 {len(results)} ta anime topildi\nTanlang 👇",
        reply_markup=kb
    )

    await state.clear()


# 🔢 CODE BOYICHA
async def code_qidir(message: Message, state: FSMContext):
    code = message.text.strip()

    anime = anime_collection.find_one({"code": code})

    if not anime:
        await message.answer("❌ Bunday code yo‘q")
        return

    # Inline tugma (Yuklash)
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎬 Yuklash",
                    callback_data=f"anime_{code}_1"
                )
            ]
        ]
    )

    caption = (
        f"🎬 *{anime['nomi']}*\n"
        f"🎞 Qismi: {anime['qismi']}\n"
        f"🗓 Yili: {anime['yili']}\n"
        f"🔢 Code: {anime['code']}"
    )

    await message.answer_photo(
        photo=anime["photo"],
        caption=caption,
        parse_mode="Markdown",
        reply_markup=kb
    )

    await state.clear()


# ⏲ YIL BOYICHA
async def yil_qidir(message: Message, state: FSMContext):
    text = message.text.strip()

    results = list(anime_collection.find({
        "yili": int(text)
    }))

    if not results:
        await message.answer("❌ Bu yil bo‘yicha topilmadi")
        return

    search_cache[message.from_user.id] = results

    kb = generate_search_buttons(results)

    await message.answer(
        f"📅 {len(results)} ta anime topildi\nTanlang 👇",
        reply_markup=kb
    )

    await state.clear()


# 🔄 PAGINATION
@rt.callback_query(F.data.startswith("page_"))
async def paginate(call: CallbackQuery):
    start = int(call.data.split("_")[1])

    results = search_cache.get(call.from_user.id, [])

    kb = generate_search_buttons(results, start=start)

    await call.message.edit_reply_markup(reply_markup=kb)

@rt.callback_query(F.data.startswith("info_"))
async def anime_info(call: CallbackQuery):
    code = call.data.split("_")[1]

    anime = anime_collection.find_one({"code": code})

    if not anime:
        await call.answer("Topilmadi", show_alert=True)
        return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎬 Yuklash",
                    callback_data=f"anime_{code}_1"  # 🔥 1-qismdan boshlaydi
                )
            ]
        ]
    )

    caption = f"""
🎬 *{anime['nomi']}*

🎞 Qismlar: {anime['qismi']}
🎭 Janr: {anime['janr']}
🗓 Yili: {anime['yili']}
🔢 Code: `{anime['code']}`
"""

    await call.message.answer_photo(
        photo=anime["photo"],
        caption=caption,
        reply_markup=kb,
        parse_mode="Markdown"
    )

# Obuna tugmasi
@rt.callback_query(F.data.startswith("subscribe_"))
async def subscribe_video(call: CallbackQuery):
    _, code, qism = call.data.split("_")
    user_id = call.from_user.id

    # Tekshirish: foydalanuvchi allaqachon obuna bo‘lganmi
    if subscribers_collection.find_one({"user_id": user_id, "code": code, "nomi": qism}):
        await call.answer("Siz bu amalni allaqachon bajardingiz ✅", show_alert=True)
        return

    subscribers_collection.insert_one({"user_id": user_id, "code": code, "nomi": qism})
    await call.answer("Obunangiz saqlandi ✅", show_alert=True)

# Saqlash tugmasi
@rt.callback_query(F.data.startswith("save_"))
async def save_video(call: CallbackQuery):
    _, code, qism = call.data.split("_")
    user_id = call.from_user.id

    if saved_collection.find_one({"user_id": user_id, "code": code, "nomi": qism}):
        await call.answer("Siz bu amalni allaqachon bajardingiz ✅", show_alert=True)
        return

    saved_collection.insert_one({"user_id": user_id, "code": code, "nomi": qism})
    await call.answer("Video saqlandi 💾", show_alert=True)

# O‘chirish tugmasi
@rt.callback_query(F.data.startswith("delete_"))
async def delete_video(call: CallbackQuery, bot: Bot):
    _, code, qism = call.data.split("_")
    chat_id = call.message.chat.id
    msg_id = call.message.message_id

    await bot.delete_message(chat_id, msg_id)
    await call.answer("Video o‘chirildi 🗑", show_alert=True)

async def islash(message: Message):
    await message.answer('*Izlash bolimiga hush kelibsiz ozingizga kerakli izlash turini tanlang*', parse_mode="Markdown", reply_markup=izlashuchun)

# --- Inline query: tanlaganda to'g'ridan-to'g'ri rasm va caption yuborish ---
import re
from aiogram import F
from aiogram.types import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message
)

# --- INLINE: foydalanuvchi tanlaganda chatga caption + "🔢 Kod: <code>" yuboradi ---
@rt.inline_query()
async def inline_handler(inline_query, bot: Bot):
    query = inline_query.query.lower()
    results = []
    user_id = inline_query.from_user.id

    data = anime_collection.find({
        "nomi": {"$regex": query, "$options": "i"}
    }).limit(20)

    bot_username = await bot.get_me()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎬 Animelar",
                    url=f"https://t.me/{bot_username.username}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 Referal",
                    switch_inline_query=f"t.me/{bot_username.username}?start=giwey_{user_id}"
                )
            ]
        ]
    )

    for anime in data:
        caption = (
            f"🎬 <b>{anime['nomi']}</b>\n\n"
            f"📺 <b>Qism:</b> {anime.get('qismi','-')}\n"
            f"📅 <b>Yili:</b> {anime.get('yili','-')}\n"
            f"🌍 <b>Tili:</b> {anime.get('tili','-')}\n"
            f"🎭 <b>Janr:</b> {anime.get('janr','-')}\n\n"
            f"✨Rasmi: {anime['photo']}\n\n"
            f"🔢 Kod: {anime['code']}"
            # inline orqali yuboriladigan kod qatori
        )

        results.append(
            InlineQueryResultArticle(
                id=str(anime["code"]),
                title=f"{anime['nomi']} 🎬",
                description=f"📺 Qism: {anime.get('qismi','-')} | 📅 Yili: {anime.get('yili','-')} | 🧾Tili: {anime.get('tili','-')}| 🗃Code: {anime.get('code','-')}",
                input_message_content=InputTextMessageContent(
                    message_text=caption,
                    parse_mode="HTML"
                ),
                thumb_url=anime.get("photo"),
                reply_markup=keyboard
            )
        )

    await inline_query.answer(results, cache_time=1)


# --- MESSAGE HANDLER: inline orqali chatga kelgan xabarni ushlaydi,
#     "🔢 Kod: ..." ni ajratib olib, xabarni o'chirib (agar mumkin bo'lsa),
#     va anime rasmini + captionni (kod jo'natmasdan) yuboradi. ---
@rt.message(F.text & F.text.contains("🔢 Kod"))
async def handle_inline_posted(message: Message):

    text = message.text or ""
    # kodni regex bilan ajratib olamiz (kod bo'shliq yoki satr oxirigacha)
    m = re.search(r"🔢\s*Kod\s*:\s*([^\s\n]+)", text)
    if not m:
        return  # kod topilmasa chiqib ketamiz

    code = m.group(1).strip()

    # captiondan "🔢 Kod: ..." qatorini olib tashlaymiz
    caption_without_code = re.sub(r"\n?\s*🔢\s*Kod\s*:\s*[^\n]+\s*$", "", text).strip()

    # DBdan anime info olamiz
    anime = anime_collection.find_one({"code": code})
    b = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Yuklash♻", callback_data=f"nomi_{anime['code']}_1")
            ]
        ]
    )
    if not anime:
        # kod DBda yo'q bo'lsa — userga ogohlantirish (yoki xabarni o'chirish)
        try:
            await message.delete()
        except Exception:
            # guruhda delete huquqi yo'q bo'lsa, javob beramiz
            await message.reply("❌ Bunday kod topilmadi.")
            return
        await message.answer("❌ Bunday kod topilmadi.")
        return

    # O'chirishga harakat qilamiz (guruhda botga ruxsat bo'lsa ishlaydi)
    try:
        await message.delete()
    except Exception:
        # o'chirish imkoni bo'lmasa — davom etamiz, faqat foydalanuvchiga shuni eslatamiz emas,
        # balki shunchaki rasm + ma'lumotni yuboramiz. (bot boshqa foydalanuvchining xabarini edit qila olmaydi)
        pass





    # Yakuniy caption — kod qatori yo'q (siz xohlagan format)
    final_caption = (
        caption_without_code
        if caption_without_code
        else (
            f"🎬 <b>{anime.get('nomi','-')}</b>\n\n"
            f"📺 <b>Qism:</b> {anime.get('qismi','-')}\n"
            f"📅 <b>Yili:</b> {anime.get('yili','-')}\n"
            f"🌍 <b>Tili:</b> {anime.get('tili','-')}\n"
            f"🎭 <b>Janr:</b> {anime.get('janr','-')}"
        )
    )

    # Rasmini yuboramiz (photo maydoni URL yoki telegram file_id bo'lishi mumkin)
    try:
        await message.answer_photo(photo=anime.get("photo"), caption=final_caption, parse_mode="HTML", reply_markup=b)
    except Exception as e:
        # agar photo yuborilmasa oddiy matn bilan yuboramiz
        await message.answer(final_caption)

    # Qo'shimcha: agar siz kodni loglash yoki analytics qilmoqchi bo'lsangiz:
    # print(f"Inline code used: {code} by user {message.from_user.id}")


rt.message.register(islash, F.text == "🔍anime izlash")
rt.callback_query.register(nomi_izlash, F.data == "izlash")
rt.callback_query.register(janr_izlash, F.data == "janr")
rt.callback_query.register(code_izlash, F.data == "code")
rt.callback_query.register(yil_izlash, F.data == "Yil")
rt.callback_query.register(random_anime, F.data == "random")
rt.callback_query.register(kop_korilgan, F.data == "kop")
rt.callback_query.register(top_anime, F.data == "Top")
rt.message.register(nomi_qidir, Statelar.nomi1.nomi)
rt.message.register(janr_qidir, Statelar.janrlar.janr)
rt.message.register(code_qidir, Statelar.code1.code)
rt.message.register(yil_qidir, Statelar.Yili.yili)
# Router
rt.callback_query.register(send_anime, F.data.startswith("anime_"))
rt.callback_query.register(yuklash_anime, F.data.startswith("nomi_"))
rt.callback_query.register(next_qism, F.data.startswith("next_"))
rt.callback_query.register(prev_qism, F.data.startswith("prev_"))
