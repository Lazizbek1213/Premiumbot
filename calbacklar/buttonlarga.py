# ================== IMPORTLAR ==================
from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery, Message,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database.mongobase import anime_collection, qsmi_collection, kundalik_collection
import asyncio
import time

rt = Router()

# ================== STATES ==================
class KundalikState(StatesGroup):
    code = State()
    choose_type = State()
    qism = State()
    time_type = State()
    time_value = State()


# ================== TUGMA ==================
def kundalik_button():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📅 Kundaligim", callback_data="kundalik")]
        ]
    )


# ================== 1. START ==================
@rt.callback_query(F.data == "kundalik")
async def kundalik_start(call: CallbackQuery, state: FSMContext):
    await state.set_state(KundalikState.code)
    await call.message.answer("📅 Qaysi anime kodini kiriting?")


# ================== 2. CODE ==================
@rt.message(KundalikState.code)
async def get_code(message: Message, state: FSMContext):
    code = message.text.strip()

    anime = anime_collection.find_one({"code": code})
    if not anime:
        await message.answer("❌ Bunday anime topilmadi!")
        return

    await state.update_data(code=code)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎬 Anime", callback_data="kund_anime"),
                InlineKeyboardButton(text="🎞 Qism", callback_data="kund_qism")
            ]
        ]
    )

    await state.set_state(KundalikState.choose_type)

    await message.answer(
        f"🎬 {anime.get('nomi')}\n\nQanday qo‘shmoqchisiz?",
        reply_markup=kb
    )


# ================== 3. TYPE TANLASH ==================
@rt.callback_query(KundalikState.choose_type, F.data == "kund_anime")
async def choose_anime(call: CallbackQuery, state: FSMContext):
    await state.update_data(type="anime")

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⏱ Minut", callback_data="time_minut"),
                InlineKeyboardButton(text="🕐 Soat", callback_data="time_soat")
            ],
            [
                InlineKeyboardButton(text="📅 Hafta", callback_data="time_hafta"),
                InlineKeyboardButton(text="🗓 Oy", callback_data="time_oy")
            ]
        ]
    )

    await state.set_state(KundalikState.time_type)
    await call.message.answer("⏰ Qachon eslatay?", reply_markup=kb)


@rt.callback_query(KundalikState.choose_type, F.data == "kund_qism")
async def choose_qism(call: CallbackQuery, state: FSMContext):
    await state.update_data(type="qism")

    await state.set_state(KundalikState.qism)
    await call.message.answer("🎞 Qaysi qism? (raqam yozing)")


# ================== 4. QISM ==================
@rt.message(KundalikState.qism)
async def get_qism(message: Message, state: FSMContext):
    try:
        qism = int(message.text)
    except:
        await message.answer("❌ Raqam kiriting!")
        return

    await state.update_data(qism=qism)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⏱ Minut", callback_data="time_minut"),
                InlineKeyboardButton(text="🕐 Soat", callback_data="time_soat")
            ],
            [
                InlineKeyboardButton(text="📅 Hafta", callback_data="time_hafta"),
                InlineKeyboardButton(text="🗓 Oy", callback_data="time_oy")
            ]
        ]
    )

    await state.set_state(KundalikState.time_type)
    await message.answer("⏰ Qachon eslatay?", reply_markup=kb)


# ================== 5. TIME TYPE ==================
@rt.callback_query(KundalikState.time_type, F.data.startswith("time_"))
async def choose_time_type(call: CallbackQuery, state: FSMContext):
    t = call.data.split("_")[1]

    await state.update_data(time_type=t)

    await state.set_state(KundalikState.time_value)
    await call.message.answer(f"⏱ Nechi {t}?")


# ================== 6. TIME VALUE ==================
@rt.message(KundalikState.time_value)
async def save_time(message: Message, state: FSMContext):
    try:
        value = int(message.text)
    except:
        await message.answer("❌ Raqam kiriting!")
        return

    data = await state.get_data()

    seconds = {
        "minut": value * 60,
        "soat": value * 3600,
        "hafta": value * 604800,
        "oy": value * 2592000
    }[data["time_type"]]

    remind_time = int(time.time()) + seconds

    kundalik_collection.insert_one({
        "user_id": message.from_user.id,
        "code": data["code"],
        "qism": data.get("qism"),
        "type": data["type"],
        "time": remind_time
    })

    await message.answer("✅ Kundalikka saqlandi!")
    await state.clear()



# ================== 7. REMINDER WORKER ==================
async def reminder_worker(bot: Bot):
    while True:
        now = int(time.time())

        tasks = list(kundalik_collection.find({"time": {"$lte": now}}))

        for task in tasks:
            user_id = task["user_id"]
            code = task["code"]

            anime = anime_collection.find_one({"code": code})
            YUklash = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="Yuklash♻", callback_data=f"nomi_{code}")
                    ]
                ]
            )

            if task["type"] == "anime":
                await bot.send_photo(
                    chat_id=user_id,
                    photo=anime["photo"],
                    caption=f"🎬 {anime['nomi']}\n*⏰ Eslatma vaqti keldi! Yuklab olish uchun tugmadan foydalaning*✨",
                    parse_mode="Markdown",
                    reply_markup=YUklash
                )

            else:
                qsim = qsmi_collection.find_one({
                    "code": code,
                    "qsimi": task["qism"]
                })

                await bot.send_video(
                    chat_id=user_id,
                    video=qsim["url"],
                    caption=f"🎬 {anime['nomi']}\n🎞 Qism: {task['qism']} *maroqli hordiq✅*",
                    parse_mode="Markdown"
                )

            kundalik_collection.delete_one({"_id": task["_id"]})

        await asyncio.sleep(10)


# ================== MAIN ==================
# asyncio.create_task(reminder_worker(bot))