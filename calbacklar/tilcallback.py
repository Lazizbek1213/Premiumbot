from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery

from database.mongobase import tili_collection

rt = Router()


@rt.callback_query(F.data == "uz")
async def uzbek_language(call: CallbackQuery, bot: Bot):

    user_id = call.from_user.id

    tili_collection.update_one(
        {"user_id": user_id},
        {"$set": {"lang": "uz"}},
        upsert=True
    )

    await bot.send_message(
        chat_id=call.message.chat.id,
        text="🇺🇿 Til o'zbek tiliga o'zgartirildi"
    )


@rt.callback_query(F.data == "eng")
async def english_language(call: CallbackQuery, bot: Bot):

    user_id = call.from_user.id

    tili_collection.update_one(
        {"user_id": user_id},
        {"$set": {"lang": "eng"}},
        upsert=True
    )

    await bot.send_message(
        chat_id=call.message.chat.id,
        text="🇬🇧 Language changed to English"
    )


@rt.callback_query(F.data == "ru")
async def russian_language(call: CallbackQuery, bot: Bot):

    user_id = call.from_user.id

    tili_collection.update_one(
        {"user_id": user_id},
        {"$set": {"lang": "ru"}},
        upsert=True
    )

    await bot.send_message(
        chat_id=call.message.chat.id,
        text="🇷🇺 Язык изменён на русский"
    )


@rt.callback_query(F.data == "ar")
async def arabic_language(call: CallbackQuery, bot: Bot):

    user_id = call.from_user.id

    tili_collection.update_one(
        {"user_id": user_id},
        {"$set": {"lang": "ar"}},
        upsert=True
    )

    await bot.send_message(
        chat_id=call.message.chat.id,
        text="🇸🇦 تم تغيير اللغة إلى العربية"
    )