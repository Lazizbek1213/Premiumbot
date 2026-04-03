from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from Inlinebutton import nastroyka_menu

rt = Router()

@rt.message(F.text == "⚙ Nastroyka")
async def open_nastroyka(msg: Message):
    if msg.text == "⚙ Nastroyka":
        await msg.answer(
            "⚙ Nastroyka menyusi",
            reply_markup=nastroyka_menu(1)
        )

@rt.callback_query(F.data == "ortga1")
async def open_nastroyka(call: CallbackQuery):
        await call.message.edit_text(
            "⚙ Nastroyka menyusi",
            reply_markup=nastroyka_menu(1)
        )

# ================================
# CALLBACK HANDLER – SAHIFA ALMASHTIRISH
# ================================
@rt.callback_query(F.data.startswith("menu_"))
async def menu_callback(call: CallbackQuery):
    # Sahifa almashtirish
    if call.data.startswith("menu_"):
        page = int(call.data.split("_")[1])
        await call.message.edit_reply_markup(reply_markup=nastroyka_menu(page))
