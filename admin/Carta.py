from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from Inlinebutton import adminpaneltug
from database.mongobase import get_carta, add_carta
from Statelar import CartaState


rt = Router()


def carta_menu():
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Carta qo'shish", callback_data="add_carta")],
            [InlineKeyboardButton(text="🔙 Ortga", callback_data="back_admin")]
        ]
    )
    return kb


@rt.callback_query(F.data == "carta")
async def carta_panel(call: CallbackQuery):

    carta = get_carta()

    if carta:
        text = f"💳 *Hozirgi carta*\n\n`{carta['number']}`"
    else:
        text = "⚠️ Carta hali qo'shilmagan"

    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=carta_menu())


@rt.callback_query(F.data == "add_carta")
async def carta_add(call: CallbackQuery, state: FSMContext):

    await call.message.edit_text(
        "💳 *Yangi carta raqamini yuboring*\n\n"
        "Misol:\n`8600 1234 5678 9012`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Ortga", callback_data="back_admin")]
            ]
        )
    )

    await state.set_state(CartaState.add)
    await call.answer()


@rt.message(CartaState.add)
async def carta_save(msg: Message, state: FSMContext):

    number = msg.text

    add_carta(number)

    await msg.answer(
        f"✅ *Carta muvaffaqiyatli qo'shildi*\n\n`{number}`",
        parse_mode="Markdown",
        reply_markup=carta_menu()
    )

    await state.clear()


@rt.callback_query(F.data == "back_admin")
async def back_admin(call: CallbackQuery):

    await call.message.edit_text(
        "*admin tugmalari marhamat nima qilmoqchisiz 📌✒*",
        reply_markup=adminpaneltug, parse_mode="Markdown"
    )