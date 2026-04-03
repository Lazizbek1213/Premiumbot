from aiogram import Router, F, Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database.mongobase import admin_calleks, user_collection
from Filters.Filtirlar import IsAdmin
from Inlinebutton import adminpaneltug
import Statelar
import asyncio
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

rt = Router()

admintugma = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Admin qo'shish 🔐", callback_data="qoshish")],
        [InlineKeyboardButton(text="Admin o'chirish 🔓", callback_data="ochirish")],
        [InlineKeyboardButton(text="Ortga ▶", callback_data="Ortga")]
    ]
)

async def admintugmalri(message: Message):
    await message.answer("*admin tugmalari marhamat nima qilmoqchisiz 📌✒*", reply_markup=adminpaneltug, parse_mode="Markdown")

async def adminpanel(call: CallbackQuery):
    await call.message.answer("💌 Salom admin, kerakli tugmani tanlang", reply_markup=admintugma)

async def adminqoshish(call: CallbackQuery, state: FSMContext):
    await call.message.answer("🧨 Admin IDsini yuboring")
    await state.set_state(Statelar.adminjon1.adminnomi)

async def adminqoshish1(message: Message, state: FSMContext):
    if message.text.isdigit():
        admin_calleks.insert_one({'qoshdi': message.from_user.first_name, 'user_id': int(message.text)})
        await message.answer("🎈 Yangi admin qo‘shildi!")
        await state.clear()
    else:
        await message.answer("❌ Iltimos, admin ID faqat raqam bo‘lishi kerak!")

async def adminochir(call: CallbackQuery, state: FSMContext):
    await call.message.answer("💔 Admin IDsini yuboring")
    await state.set_state(Statelar.adminbek.adminol)

async def adminochir1(message: Message, state: FSMContext):
    if message.text.isdigit():
        admin_id = int(message.text)
        result = admin_calleks.delete_one({'user_id': admin_id})
        if result.deleted_count > 0:
            await message.answer("✅ Admin o‘chirildi")
        else:
            await message.answer("❌ Bu ID bo‘yicha admin topilmadi")
        await state.clear()
    else:
        await message.answer("❌ Admin ID faqat raqam bo‘lishi kerak!")

async def meniidim(message: Message):
    await message.answer(f"Sizning IDingiz: <b>{message.from_user.id}</b>", parse_mode="HTML")

async def orqaga(call: CallbackQuery):
    await call.message.edit_text("*admin tugmalari marhamat nima qilmoqchisiz 📌✒*", reply_markup=adminpaneltug, parse_mode="Markdown")


from aiogram.fsm.state import StatesGroup, State

class BroadcastState(StatesGroup):
    message = State()

@rt.callback_query(F.data == "Habarga")
async def start_broadcast(call: CallbackQuery, state: FSMContext):
    # faqat admin tekshirish (o‘zing qo‘shasan)
    await state.set_state(BroadcastState.message)
    await call.message.answer("✍️ Yubormoqchi bo‘lgan xabaringizni yozing:")

@rt.message(BroadcastState.message)
async def send_broadcast(message: Message, state: FSMContext, bot: Bot):

    users = user_collection.find({})

    success = 0
    blocked = 0
    failed = 0

    # original buttonni olish
    markup = message.reply_markup

    for user in users:
        user_id = user.get("user")

        try:
            # ================== TEXT ==================
            if message.text:
                await bot.send_message(
                    chat_id=user_id,
                    text=message.text,
                    reply_markup=markup
                )

            # ================== PHOTO ==================
            elif message.photo:
                await bot.send_photo(
                    chat_id=user_id,
                    photo=message.photo[-1].file_id,
                    caption=message.caption,
                    reply_markup=markup
                )

            # ================== VIDEO ==================
            elif message.video:
                await bot.send_video(
                    chat_id=user_id,
                    video=message.video.file_id,
                    caption=message.caption,
                    reply_markup=markup
                )

            success += 1

        except TelegramForbiddenError:
            blocked += 1

        except Exception:
            failed += 1

    await message.answer(
        f"""<blockquote>📊 <b>Natija</b></blockquote>

✅ Yuborildi: {success}
🚫 Block: {blocked}
❌ Xatolik: {failed}
""",
        parse_mode="HTML"
    )

    await state.clear()

# Register handlers
rt.callback_query.register(orqaga, F.data == "Ortga")
rt.callback_query.register(adminpanel, F.data == "adminli")
rt.message.register(admintugmalri, Command("admin"), IsAdmin())
rt.callback_query.register(adminqoshish, F.data == "qoshish")
rt.message.register(adminqoshish1, Statelar.adminjon1.adminnomi)
rt.callback_query.register(adminochir, F.data == "ochirish")
rt.message.register(adminochir1, Statelar.adminbek.adminol)
rt.message.register(meniidim, F.text == "/id")