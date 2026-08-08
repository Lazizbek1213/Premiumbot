from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.mongobase import user_collection
from Inlinebutton import adminpaneltug
from database.mongobase import promokod_collektion, admin_calleks, user_collection
from datetime import datetime, timedelta, timezone
import asyncio
import random
import Statelar
import string
from pymongo import ReturnDocument
from Inlinebutton import nastroyka_menu

rt = Router()


# STATES
class AdminBalance(StatesGroup):
    user_id = State()
    amount = State()

# ADMIN KEYBOARD
admin_balance = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💰 Pul qo'shish", callback_data="bal_add"), InlineKeyboardButton(text="❌ Pul ayirish", callback_data="bal_remove")],
        [
            InlineKeyboardButton(text="Admin boshqaruvi🛠", callback_data="adminboshqa"), InlineKeyboardButton(text="Yuklash turi⁉", callback_data="Yuklashgatur")
        ],
        [
            InlineKeyboardButton(text="Promokod💳", callback_data="promo"), InlineKeyboardButton(text="Kanalqoshib qoyish🆔", callback_data='Postkanal')
        ],
        [
            InlineKeyboardButton(text="HabarYuborish🧾", callback_data="Habarga")
        ],
        [
            InlineKeyboardButton(text="Ortga◀", callback_data="Ortga2")
        ]
    ]
)

# NASTROYKA MENU
async def nastroyka(call: CallbackQuery):
        await call.message.edit_text(
            "*Adminlar Nastroykasi📌*",
            parse_mode="Markdown",
            reply_markup=admin_balance
        )

# ADD yoki REMOVE tanlash
async def balance_action(call: CallbackQuery, state: FSMContext):
    action = call.data.split("_")[1]

    await state.update_data(action=action)

    await call.message.answer("User ID yuboring:")
    await state.set_state(AdminBalance.user_id)

# USER ID olish
async def get_user_id(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("User ID faqat raqam bo'lishi kerak")
        return

    await state.update_data(user_id=int(msg.text))

    await msg.answer("Pul miqdorini kiriting:")
    await state.set_state(AdminBalance.amount)

# BALANCE UPDATE
async def process_balance(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("Miqdor faqat raqam bo'lishi kerak")
        return

    data = await state.get_data()

    user_id = data["user_id"]
    action = data["action"]
    amount = int(msg.text)

    user = user_collection.find_one({"user": user_id})

    if not user:
        await msg.answer("User topilmadi")
        await state.clear()
        return

    balance = user.get("balance", 0)

    if action == "add":
        new_balance = balance + amount
        text = f"💰 {amount} so'm qo'shildi"
    else:
        new_balance = balance - amount
        text = f"❌ {amount} so'm ayirildi"

    user_collection.update_one(
        {"user": user_id},
        {"$set": {"balance": new_balance}}
    )

    await msg.answer(
        f"User: {user_id}\n{text}\nYangi balans: {new_balance}"
    )

    await state.clear()

async def Ortga(call: CallbackQuery):
    await call.message.edit_text("*admin tugmalari marhamat nima qilmoqchisiz 📌✒*", parse_mode="Markdown", reply_markup=adminpaneltug)





# 1️⃣ Admin "Promokod💳" tugmasini bosganda
time_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="⏱ Minut", callback_data="time_unit_minute"),
            InlineKeyboardButton(text="⏰ Soat", callback_data="time_unit_hour")
        ],
        [
            InlineKeyboardButton(text="📅 Kun", callback_data="time_unit_day"),
            InlineKeyboardButton(text="📆 Hafta", callback_data="time_unit_week")
        ],
        [
            InlineKeyboardButton(text="🗓 Oy", callback_data="time_unit_month")
        ]
    ]
)

# ================== 1. BOSHLASH ==================
@rt.callback_query(F.data == "promo")
async def start_promo(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Promo kod nomini kiriting:")
    await state.set_state(Statelar.PromoStates.waiting_code_name)


# ================== 2. NOM ==================
@rt.message(Statelar.PromoStates.waiting_code_name)
async def promo_name(msg: Message, state: FSMContext):
    await state.update_data(promo_name=msg.text)
    await msg.answer("Balansga qo‘shiladigan miqdorni kiriting (raqam):")
    await state.set_state(Statelar.PromoStates.waiting_amount)


# ================== 3. MIQDOR ==================
@rt.message(Statelar.PromoStates.waiting_amount)
async def promo_amount(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("❌ Iltimos, faqat raqam kiriting!")
        return

    await state.update_data(amount=int(msg.text))
    await msg.answer(
        "Promo kod qancha vaqtga amal qiladi?",
        reply_markup=time_keyboard
    )
    await state.set_state(Statelar.PromoStates.waiting_time_unit)


# ================== 4. TIME UNIT ==================
@rt.callback_query(Statelar.PromoStates.waiting_time_unit)
async def promo_time_unit(call: CallbackQuery, state: FSMContext):

    unit_map = {
        "time_unit_minute": "minutes",   # 🔥 qo‘shildi
        "time_unit_hour": "hours",
        "time_unit_day": "days",
        "time_unit_week": "weeks",
        "time_unit_month": "months"
    }

    selected_unit = unit_map.get(call.data)

    if not selected_unit:
        await call.answer("❌ Xato tanlov!", show_alert=True)
        return

    await state.update_data(time_unit=selected_unit)

    await call.message.answer(
        f"Necha {selected_unit} davomida amal qiladi? (raqam kiriting)"
    )

    await state.set_state(Statelar.PromoStates.waiting_time_value)


# ================== 5. CREATE PROMO ==================
@rt.message(Statelar.PromoStates.waiting_time_value)
async def promo_time_value(msg: Message, state: FSMContext):

    if not msg.text.isdigit():
        await msg.answer("❌ Iltimos, faqat raqam kiriting!")
        return

    time_value = int(msg.text)

    data = await state.get_data()
    promo_name = data["promo_name"]
    amount = data["amount"]
    time_unit = data["time_unit"]

    # 🔑 random promo code
    promo_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    now = datetime.now()
    expire = now

    # 🔥 TIME LOGIC
    if time_unit == "minutes":
        expire += timedelta(minutes=time_value)
    elif time_unit == "hours":
        expire += timedelta(hours=time_value)
    elif time_unit == "days":
        expire += timedelta(days=time_value)
    elif time_unit == "weeks":
        expire += timedelta(weeks=time_value)
    elif time_unit == "months":
        expire += timedelta(days=time_value * 30)

    # 💾 SAVE DB
    promokod_collektion.insert_one({
        "promo_name": promo_name,
        "promo_code": promo_code,
        "amount": amount,
        "created_at": now,
        "expire_at": expire,
        "used_by": []
    })

    await msg.answer(
        f"✅ Promo kod yaratildi!\n\n"
        f"📌 Nom: {promo_name}\n"
        f"🔑 Kod: {promo_code}\n"
        f"💰 Balans: +{amount}\n"
        f"⏰ Tugash vaqti:\n{expire.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    await state.clear()


# ================== 6. ISHLATISH BOSHLASH ==================
@rt.callback_query(F.data == "promokobonus")
async def start_use_promo(call: CallbackQuery, state: FSMContext):
    await call.message.answer("🔑 Promo kodni kiriting:")
    await state.set_state(Statelar.Promokodish.ishlatish)


# ================== 7. ISHLATISH ==================
@rt.message(Statelar.Promokodish.ishlatish)
async def apply_promo(msg: Message, state: FSMContext):

    user_id = msg.from_user.id

    promo = promokod_collektion.find_one({
        "promo_code": msg.text.strip().upper()
    })

    if not promo:
        await msg.answer("❌ Bunday promo kod topilmadi.")
        return

    # ⏰ vaqt tekshirish
    now = datetime.now()
    if promo["expire_at"] <= now:
        await msg.answer("⏰ Promo kod muddati tugagan.")
        return

    # 🔁 ishlatilganmi
    if user_id in promo.get("used_by", []):
        await msg.answer("⚠ Siz bu promo kodni ishlatgansiz.")
        return

    # 💰 balans qo‘shish
    user = user_collection.find_one_and_update(
        {"user": user_id},
        {"$inc": {"balance": promo["amount"]}},
        return_document=ReturnDocument.AFTER
    )

    # 📌 used list
    promokod_collektion.update_one(
        {"_id": promo["_id"]},
        {"$push": {"used_by": user_id}}
    )

    await msg.answer(
        f"✅ Promo ishladi!\n\n"
        f"💰 +{promo['amount']} qo‘shildi\n"
        f"💳 Yangi balans: {user['balance']}"
    )

    await state.clear()

ortga = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Ortga◀", callback_data="Ortga7")
        ]
    ]
)

@rt.callback_query(F.data == "reklama")
async def reklama_panel(call: CallbackQuery):

    await call.message.edit_text(
        "📢 Reklama boyicha boglanish @khaytbyv",
        reply_markup=ortga
    )

@rt.callback_query(F.data == "stat")
async def users_count(call: CallbackQuery):
    count = user_collection.count_documents({})
    await call.message.edit_text(f"👥 Jami foydalanuvchilar: {count}", reply_markup=ortga)


@rt.callback_query(F.data == "Ortga7")
async def Ortga1(call: CallbackQuery):
    await call.message.edit_text('⚙️ Nastroyka menyusi', reply_markup=nastroyka_menu(3))


# REGISTER
rt.callback_query.register(Ortga, F.data == "Ortga2")
rt.callback_query.register(nastroyka, F.data == "nastroy")
rt.callback_query.register(balance_action, F.data.startswith("bal_"))
rt.message.register(get_user_id, AdminBalance.user_id)
rt.message.register(process_balance, AdminBalance.amount)