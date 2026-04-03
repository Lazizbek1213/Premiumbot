# file: Shorts.py
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaVideo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import random

from database.mongobase import short_collection, anime_collection, korishlar_collection

rt = Router()

# ================== STATE ==================
class ShortState(StatesGroup):
    video = State()
    caption = State()
    code = State()

# ================== CACHE ==================
user_shorts = {}

# ================== ADMIN: BOSHLASH ==================
@rt.callback_query(F.data == "short_add")
async def start_short(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("🎬 *1 ta short video yuboring:*", parse_mode="Markdown")
    await state.set_state(ShortState.video)

# ================== VIDEO ==================
@rt.message(ShortState.video)
async def short_video(msg: Message, state: FSMContext):
    if not msg.video:
        await msg.answer("❌ *Iltimos, video yuboring!*", parse_mode="Markdown")
        return

    await state.update_data(video=msg.video.file_id)
    await msg.answer("✍️ *Qisqacha sharh yozing:*", parse_mode="Markdown")
    await state.set_state(ShortState.caption)

# ================== CAPTION ==================
@rt.message(ShortState.caption)
async def short_caption(msg: Message, state: FSMContext):
    await state.update_data(caption=msg.text)
    await msg.answer("🔢 *Endi short uchun kod kiriting:*", parse_mode="Markdown")
    await state.set_state(ShortState.code)

# ================== SAVE ==================
@rt.message(ShortState.code)
async def short_save(msg: Message, state: FSMContext):
    data = await state.get_data()
    short_collection.insert_one({
        "video": data["video"],
        "caption": data["caption"],
        "code": msg.text
    })
    await msg.answer("✅ *Short muvaffaqiyatli yuklandi!* 🚀", parse_mode="Markdown")
    await state.clear()

# ================== USER: BOSHLASH ==================
@rt.callback_query(F.data == "shorts")
async def start_watch_short(call: CallbackQuery):
    shorts = list(short_collection.find())
    if not shorts:
        await call.message.edit_text("❌ Hozircha shortlar yo‘q", parse_mode="Markdown")
        return

    random.shuffle(shorts)
    user_shorts[call.from_user.id] = {
        "list": shorts,
        "index": 0
    }

    short = shorts[0]
    await send_short(call, short)

# ================== SEND SHORT ==================
async def send_short(call: CallbackQuery, short):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎬 Tomosha qilish", callback_data=f"short_open_{short['code']}")],
            [
                InlineKeyboardButton(text="◀️", callback_data="short_prev"),
                InlineKeyboardButton(text="▶️", callback_data="short_next")
            ]
        ]
    )

    media = InputMediaVideo(
        media=short["video"],
        caption=f"✨ {short['caption']}",
        parse_mode="Markdown"
    )

    await call.message.edit_media(media=media, reply_markup=kb)

# ================== NEXT ==================
@rt.callback_query(F.data == "short_next")
async def next_short(call: CallbackQuery):
    data = user_shorts.get(call.from_user.id)
    if not data:
        return

    data["index"] += 1
    if data["index"] >= len(data["list"]):
        data["index"] = 0

    short = data["list"][data["index"]]
    await send_short(call, short)

# ================== PREV ==================
@rt.callback_query(F.data == "short_prev")
async def prev_short(call: CallbackQuery):
    data = user_shorts.get(call.from_user.id)
    if not data:
        return

    data["index"] -= 1
    if data["index"] < 0:
        data["index"] = len(data["list"]) - 1

    short = data["list"][data["index"]]
    await send_short(call, short)

# ================== TOMOSHA ==================
@rt.callback_query(F.data.startswith("short_open_"))
async def open_short(call: CallbackQuery):
    code = call.data.split("_")[2]

    anime = anime_collection.find_one({"code": code})
    korish = korishlar_collection.count_documents({"code": code})
    if not anime:
        await call.answer("❌ Video topilmadi", show_alert=True)
        return

    caption = (
        f"📋*Nomi*: {anime['nomi']}\n"
        f"🎞*Qismi*: {anime['qismi']}\n"
        f"🔣*Code*: {anime['code']}\n"
        f"🔠*Tili*: {anime['tili']}\n"
        f"🕑*Yili*: {anime['yili']}\n"
        f"*👁‍Korishlar*: {korish}"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Yuklash✅", callback_data=f"nomi_{code}")]
        ]
    )

    await call.message.answer_photo(
        photo=anime["photo"],
        caption=caption,
        parse_mode="Markdown",
        reply_markup=kb
    )