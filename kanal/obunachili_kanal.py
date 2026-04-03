from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from database.mongobase import kanal
import Statelar
import admin.adminqosh

rt = Router()

channels_collection = kanal["kanallar"]


# 1️⃣ Kanal qo'shishni boshlash
async def start_add_channel(call: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.send_message(call.from_user.id, "📢 Kanal nomini kiriting:")
    await state.set_state(Statelar.Kanal.nomi)


# 2️⃣ Kanal nomini olish
async def get_channel_name(message: Message, state: FSMContext):
    await state.update_data(channel_name=message.text)
    await message.answer("🔗 Kanal username kiriting (@ bilan):")
    await state.set_state(Statelar.Kanal.username)


# 3️⃣ Username olish
async def get_channel_username(message: Message, state: FSMContext):

    if not message.text.startswith("@"):
        return await message.answer("❌ Username @ bilan boshlanishi kerak")

    await state.update_data(channel_username=message.text)

    await message.answer("👥 Nechta obunachi kerak?")
    await state.set_state(Statelar.Kanal.sub_count)


# 4️⃣ Obunachi sonini olish va DB ga yozish
async def save_channel(message: Message, state: FSMContext, bot: Bot):

    if not message.text.isdigit():
        return await message.answer("❌ Faqat son kiriting")

    data = await state.get_data()

    channel_name = data["channel_name"]
    channel_username = data["channel_username"]
    subscriber_target = int(message.text)

    # Bot adminligini tekshirish
    try:
        bot_member = await bot.get_chat_member(channel_username, bot.id)

        if bot_member.status not in ["administrator", "creator"]:
            return await message.answer("❌ Bot kanalga admin emas")

    except:
        return await message.answer("❌ Kanal topilmadi yoki bot kanalga kira olmaydi")

    # DB ga yozish
    channels_collection.insert_one({
        "channel_name": channel_name,
        "channel_username": channel_username,
        "channel_type": "public",
        "target_subscribers": subscriber_target,
        "current_subscribers": 0
    })

    await message.answer(
        f"✅ Kanal qo'shildi\n\n"
        f"📢 {channel_name}\n"
        f"🔗 {channel_username}\n"
        f"👥 Target: {subscriber_target}"
    )

    await state.clear()


# ================= REGISTER =================

rt.callback_query.register(start_add_channel, F.data == "kanalobuna")
rt.message.register(get_channel_name, Statelar.Kanal.nomi)
rt.message.register(get_channel_username, Statelar.Kanal.username)
rt.message.register(save_channel, Statelar.Kanal.sub_count)