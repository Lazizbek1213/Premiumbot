from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.mongobase import cartas, admin_calleks, user_collection
from Statelar import Deposit

rt = Router()


@rt.callback_query(F.data == "pul")
async def deposit_start(call: CallbackQuery, state: FSMContext):

    await call.message.edit_text(
        "💰 *Hisobni to‘ldirish*\n\n"
        "Qancha pul kiritmoqchisiz?\n"
        "Misol: `10000`",
        parse_mode="Markdown"
    )

    await state.set_state(Deposit.amount)


@rt.message(Deposit.amount)
async def deposit_amount(msg: Message, state: FSMContext):

    if not msg.text.isdigit():
        await msg.answer("❌ Pul miqdori raqam bo‘lishi kerak")
        return

    amount = int(msg.text)

    card = cartas.find_one()

    if not card:
        await msg.answer("⚠️ Hozircha karta mavjud emas")
        return

    await state.update_data(amount=amount)

    await msg.answer(
        f"💳 *To‘lov uchun karta*\n\n"
        f"`{card['number']}`\n\n"
        f"💰 Miqdor: *{amount} so'm*\n\n"
        "Pul o'tkazgandan keyin chek yuboring 📸",
        parse_mode="Markdown"
    )

    await state.set_state(Deposit.check)


@rt.message(Deposit.check)
async def deposit_check(msg: Message, state: FSMContext):

    if not msg.photo:
        await msg.answer("❌ Chek rasm bo‘lishi kerak")
        return

    await state.update_data(photo=msg.photo[-1].file_id)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✍ Ha", callback_data="comment_yes"),
                InlineKeyboardButton(text="❌ Yo‘q", callback_data="comment_no")
            ]
        ]
    )

    await msg.answer("Sharh qoldirasizmi?", reply_markup=kb)


@rt.callback_query(F.data == "comment_yes")
async def comment_yes(call: CallbackQuery, state: FSMContext):

    await call.message.edit_text("✍ Sharhingizni yozing")
    await state.set_state(Deposit.comment)


@rt.callback_query(F.data == "comment_no")
async def comment_no(call: CallbackQuery, state: FSMContext, bot: Bot):

    data = await state.get_data()

    photo = data["photo"]
    amount = data["amount"]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=f"approve_{call.from_user.id}_{amount}"
                ),
                InlineKeyboardButton(
                    text="❌ Bekor qilish",
                    callback_data=f"cancel_{call.from_user.id}_{amount}"
                )
            ]
        ]
    )

    admin_list = [i["user_id"] for i in admin_calleks.find()]

    for admin in admin_list:
        await bot.send_photo(
            chat_id=admin,
            photo=photo,
            caption=
            f"💰 Yangi to‘lov\n\n"
            f"👤 User: {call.from_user.id}\n"
            f"💵 Miqdor: {amount}",
            reply_markup=keyboard
        )

    await call.message.answer("✅ Chek yuborildi")
    await state.clear()


@rt.message(Deposit.comment)
async def comment_send(msg: Message, state: FSMContext, bot: Bot):

    data = await state.get_data()

    photo = data["photo"]
    amount = data["amount"]
    comment = msg.text

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=f"approve_{msg.from_user.id}_{amount}"
                ),
                InlineKeyboardButton(
                    text="❌ Bekor qilish",
                    callback_data=f"cancel_{msg.from_user.id}_{amount}"
                )
            ]
        ]
    )

    admin_list = [i["user_id"] for i in admin_calleks.find()]

    for admin in admin_list:
        await bot.send_photo(
            chat_id=admin,
            photo=photo,
            caption=
            f"💰 Yangi to‘lov\n\n"
            f"👤 User: {msg.from_user.id}\n"
            f"💵 Miqdor: {amount}\n"
            f"📝 Sharh: {comment}",
            reply_markup=keyboard
        )

    await msg.answer("✅ Chek yuborildi")
    await state.clear()

@rt.callback_query(F.data.startswith("approve_"))
async def approve(call: CallbackQuery, bot: Bot):

    data = call.data.split("_")

    user_id = int(data[1])
    amount = int(data[2])

    user_collection.update_one(
        {"user": user_id},
        {"$inc": {"balance": amount}}
    )

    await bot.send_message(user_id, f"✅ Hisobingiz {amount} so'mga to‘ldirildi")

    await call.message.edit_caption("✅ Tasdiqlandi")


@rt.callback_query(F.data.startswith("cancel_"))
async def cancel(call: CallbackQuery, bot: Bot):

    data = call.data.split("_")

    user_id = int(data[1])

    await bot.send_message(user_id, "❌ To‘lovingiz bekor qilindi")

    await call.message.edit_caption("❌ Bekor qilindi")

@rt.callback_query(F.data == "hisob")
async def account_info(call: CallbackQuery):

    user_id = call.from_user.id
    name = call.from_user.mention_html()

    user = user_collection.find_one({"user": user_id})

    if not user:
        await call.message.answer("Hisob topilmadi")
        return

    balance = user.get("balance", 0)
    referal = user.get("referal", 0)
    bot_user = await call.message.bot.get_me()

    referal_link = f"https://t.me/{bot_user.username}?start=giwey_{user_id}"

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👥 Referal link",
                    url=referal_link
                ),
                InlineKeyboardButton(
                    text="💰 Pul kiritish",
                    callback_data="pul"
                )
            ],
            [
                InlineKeyboardButton(text="Ortga◀", callback_data="ortga1")
            ]
        ]
    )

    text = (
        f"👤 <b>Sizning hisobingiz</b>\n\n"
        f"ismingiz 📂: <b> {name} </b>\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"💰 Balans: <b>{balance}</b> so'm\n"
        f"👥 Referal: <b>{referal}</b>\n"
    )

    await call.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=kb
    )
