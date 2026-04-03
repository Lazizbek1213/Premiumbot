from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta, timezone
import asyncio
from database.mongobase import channel_vaqt, admin_calleks
from Inlinebutton import vaqt_tugma
import Statelar

# TTL indeksi (agar mavjud bo'lmasa)
expire = datetime.now(timezone.utc) + timedelta(seconds=60)
channel_vaqt.create_index("expire_at", expireAfterSeconds=0)

rt = Router()

# 1️⃣ Kanal nomini so'rash
async def vaqtk(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Kanal nomini kiriting")
    await state.set_state(Statelar.vaqtKa.vaqtK)

# 2️⃣ Kanal nomini olish
async def vaqtk1(message: Message, state: FSMContext):
    await state.update_data(nomi=message.text)
    await message.answer("Kanal username yuboring (@ bilan)")
    await state.set_state(Statelar.vaqtKa.VaqtK1)

# 3️⃣ Username olish
async def vaqtk2(message: Message, state: FSMContext):
    if not message.text.startswith("@"):
        return await message.answer("Username @ bilan boshlanishi kerak")
    await state.update_data(username=message.text)
    await message.answer("Kanal qancha vaqt majburiy bo‘ladi?", reply_markup=vaqt_tugma)

# 4️⃣ Vaqt turini tanlash
async def minut(call: CallbackQuery, state: FSMContext):
    await state.update_data(type="minut")
    await call.message.answer("Nechi minut?")
    await state.set_state(Statelar.vaqtKa.VaqtK2)

async def kun(call: CallbackQuery, state: FSMContext):
    await state.update_data(type="kun")
    await call.message.answer("Nechi kun?")
    await state.set_state(Statelar.vaqtKa.VaqtK2)

async def hafta(call: CallbackQuery, state: FSMContext):
    await state.update_data(type="hafta")
    await call.message.answer("Nechi hafta?")
    await state.set_state(Statelar.vaqtKa.VaqtK2)

async def oy(call: CallbackQuery, state: FSMContext):
    await state.update_data(type="oy")
    await call.message.answer("Nechi oy?")
    await state.set_state(Statelar.vaqtKa.VaqtK2)

# 5️⃣ Vaqtni hisoblash va DB ga yozish (sekundga o'tkazish)
async def vaqt_saqlash(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Faqat son kiriting")

    data = await state.get_data()
    son = int(message.text)
    now = datetime.now(timezone.utc)

    # Sekundlarga aylantirish
    if data["type"] == "minut":
        expire = now + timedelta(seconds=son * 60)
    elif data["type"] == "kun":
        expire = now + timedelta(seconds=son * 86400)  # 24*60*60
    elif data["type"] == "hafta":
        expire = now + timedelta(seconds=son * 604800) # 7*24*60*60
    elif data["type"] == "oy":
        expire = now + timedelta(seconds=son * 2592000) # 30*24*60*60

    # DB ga yozish
    channel_vaqt.insert_one({
        "channel_name": data["nomi"],
        "channel_username": data["username"],
        "channel_type": "public",
        "expire_at": expire
    })

    await message.answer(f"✅ Kanal vaqtli qo‘shildi, ochilishi: {expire.astimezone(timezone(timedelta(hours=5)))} (UZB vaqti)")
    await state.clear()


# 6️⃣ Routerga registratsiya
rt.callback_query.register(vaqtk, F.data == "Vaqtkanal")
rt.message.register(vaqtk1, Statelar.vaqtKa.vaqtK)
rt.message.register(vaqtk2, Statelar.vaqtKa.VaqtK1)
rt.callback_query.register(minut, F.data == "minut")
rt.callback_query.register(kun, F.data == "kun")
rt.callback_query.register(hafta, F.data == "hafta")
rt.callback_query.register(oy, F.data == "oy")
rt.message.register(vaqt_saqlash, Statelar.vaqtKa.VaqtK2)

