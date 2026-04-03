from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from Statelar import IjtimoiyState
from Inlinebutton import ijdimoiytarmoqlar, kanaltugmasi

from database.mongobase import kanal


rt = Router()

# MongoDB collection
ijtimoiy_db = kanal["ijtimoiy_links"]


# STATE
@rt.callback_query(F.data == "tarmoqde")
async def ijdimoiytug(call: CallbackQuery):
    await call.message.edit_text("*Qaysi tarmoqni Qoshmoqchisiz ✔*", reply_markup=ijdimoiytarmoqlar, parse_mode="Markdown")

@rt.callback_query(F.data == "orqadbuend")
async def ortdaz(call: CallbackQuery):
    await call.message.edit_text("*Nima qilmoqchisiz*", reply_markup=kanaltugmasi, parse_mode="Markdown")

# TUGMALAR
ijtimoiytarmoqlar = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Instagram", callback_data="insta"),
            InlineKeyboardButton(text="facebook", callback_data="face")
        ],
        [
            InlineKeyboardButton(text="Youtube", callback_data="youtub"),
            InlineKeyboardButton(text="discord", callback_data="disco")
        ]
    ]
)


# TUGMA BOSILGANDA
@rt.callback_query(F.data.in_(["instagram", "facebook", "youtube", "discord"]))
async def social_select(call: CallbackQuery, state: FSMContext):

    await state.update_data(network=call.data)

    await call.message.answer("🔗 Marhamat silka yuboring:")

    await state.set_state(IjtimoiyState.link)


# SILKA QABUL QILISH
@rt.message(IjtimoiyState.link)
async def save_social_link(message: Message, state: FSMContext):

    data = await state.get_data()

    network = data.get("network")
    link = message.text
    user_id = message.from_user.id

    # MongoDB ga saqlash (1 ta qoida)
    ijtimoiy_db.update_one(
        {
            "user_id": user_id,
            "network": network
        },
        {
            "$set": {
                "link": link
            }
        },
        upsert=True
    )

    await message.answer("✅ Silka saqlandi")

    await state.clear()