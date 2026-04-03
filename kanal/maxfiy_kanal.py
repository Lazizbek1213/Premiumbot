from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database.mongobase import kanal
import Statelar


rt = Router()


user_requests = kanal['user_requests']
user_reques = kanal['user_req']


@rt.callback_query(F.data == "kanalmax")
async def start_private(call: CallbackQuery, state: FSMContext):
    await call.message.answer("🔐 Kanal nomini kiriting:")
    await state.set_state(Statelar.privet.user)


@rt.message(Statelar.privet.user)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(channel_name=message.text)
    await message.answer("📛 Kanal username yuboring (@ bilan):")
    await state.set_state(Statelar.privet.add)


@rt.message(Statelar.privet.add)
async def get_username(message: Message, state: FSMContext):

    if not message.text.startswith("@"):
        return await message.answer("❌ Username @ bilan boshlansin")

    await state.update_data(channel_username=message.text)

    await message.answer("🔗 Invite link yuboring:")
    await state.set_state(Statelar.privet.aprivet)


@rt.message(Statelar.privet.aprivet)
async def get_link(message: Message, state: FSMContext):

    data = await state.get_data()

    user_requests.insert_one({
        "channel_name": data["channel_name"],
        "channel_username": data["channel_username"],
        "invite_link": message.text,
        "channel_type": "private"
    })

    await message.answer("✅ Maxfiy kanal qo‘shildi")
    await state.clear()

from aiogram.types import ChatJoinRequest

userlarga = kanal["user_req"]


@rt.chat_join_request()
async def join_request(req: ChatJoinRequest):

    user_reques.update_one(
        {
            "user_id": req.from_user.id,
            "channel_name": req.chat.title
        },
        {
            "$set": {
                "chat_id": req.chat.id,
                "approved": True
            }
        },
        upsert=True
    )

    await req.bot.send_message(
        req.from_user.id,
        f"✅ Siz kanalga obuna bo‘ldingiz\n{req.chat.title}"
    )

