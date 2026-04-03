from aiogram import Router, F, Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from database.mongobase import TrueFalse_Y, elon_collection, user_collection
from aiogram.fsm.context import FSMContext
from habarlar.nastroykapanel import admin_balance, adminpaneltug
import Statelar

rt = Router()

# ================== TUGMA GENERATOR ==================
def get_settings_kb(state: bool):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"Yuklash {'✅' if state else '❌'}",
                    callback_data="toggle_global"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Ortga◀",
                    callback_data="Ortga5"
                )
            ]
        ]
    )


# ================== PANELNI OCHISH ==================
@rt.callback_query(F.data == "Yuklashgatur")
async def yuklash_panel(call: CallbackQuery):

    data = TrueFalse_Y.find_one({"_id": "global"})

    if not data:
        TrueFalse_Y.insert_one({
            "_id": "global",
            "enabled": False
        })
        state = False
    else:
        state = data["enabled"]

    await call.message.edit_text(
        f"⚙️ Yuklash sozlamasi\n\nHozirgi holat: {'✅ Yoqilgan' if state else '❌ O‘chirilgan'}",
        reply_markup=get_settings_kb(state)
    )


# ================== TOGGLE ==================
@rt.callback_query(F.data == "toggle_global")
async def toggle_global(call: CallbackQuery):

    data = TrueFalse_Y.find_one({"_id": "global"})

    if not data:
        state = True
        TrueFalse_Y.insert_one({
            "_id": "global",
            "enabled": True
        })
    else:
        state = not data["enabled"]

        TrueFalse_Y.update_one(
            {"_id": "global"},
            {"$set": {"enabled": state}}
        )

    await call.message.edit_text(
        f"⚙️ Yuklash sozlamasi\n\nHozirgi holat: {'✅ Yoqilgan' if state else '❌ O‘chirilgan'}",
        reply_markup=get_settings_kb(state)
    )

    await call.answer("O‘zgartirildi ✅")


# ================== ORTGA ==================
@rt.callback_query(F.data == "Ortga5")
async def back_settings(call: CallbackQuery):
    await call.message.edit_text("*admin tugmalari marhamat nima qilmoqchisiz 📌✒️*",reply_markup=admin_balance, parse_mode="Markdown")

@rt.callback_query(F.data == "elon_add")
async def start_elon(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("📢 Elon matnini yozing:")
    await state.set_state(Statelar.ElonState.text)


# ================== ELON SAQLASH ==================
@rt.message(Statelar.ElonState.text)
async def save_elon(msg: Message, state: FSMContext):

    text = msg.text

    # 🔥 eski elonni o‘chiramiz
    elon_collection.delete_many({})

    # 💾 yangi elon saqlaymiz
    elon_collection.insert_one({
        "text": text
    })
    ortga = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Ortga◀", callback_data="Ortga6")
            ]
        ]
    )

    await msg.answer("✅ Elon saqlandi!", reply_markup=ortga)
    await state.clear()

@rt.callback_query(F.data == "Ortga6")
async def back_settings(call: CallbackQuery):
    await call.message.edit_text("*admin tugmalari marhamat nima qilmoqchisiz 📌✒️*",reply_markup=adminpaneltug, parse_mode="Markdown")


# ================== USER KO‘RADI ==================
@rt.callback_query(F.data == "elon")
async def show_elon(call: CallbackQuery):

    elon = elon_collection.find_one()

    if not elon:
        await call.answer("❌ Hozircha elon yo‘q", show_alert=True)
        return

    await call.message.answer(
        f"📢 <b>ELON</b>\n\n{elon['text']}",
        parse_mode="HTML"
    )

@rt.callback_query(F.data == "referal")
async def referal_link(call: CallbackQuery, bot: Bot):

    user_id = call.from_user.id
    bot_user = await bot.get_me()

    link = f"https://t.me/{bot_user.username}?start=giwey_{user_id}"

    user = user_collection.find_one({"user": user_id})

    referal_count = user.get("referal", 0)

    await call.message.answer(
        f"👥 Sizning referal linkingiz:\n\n{link}\n\n"
        f"👤 Taklif qilganlar: {referal_count} ta"
    )

@rt.callback_query(F.data == "A")
async def yuklashda_animeli(call: CallbackQuery):
    await call.message.edit_text(
        "*Nima qilmoqchisiz ⁉*",
        parse_mode="Markdown"
    )
