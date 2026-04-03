from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from database.mongobase import kanal, adminbase
from datetime import datetime, timezone
import Statelar
from Inlinebutton import kanaltugmasi, adminpaneltug, kanalyesno
from database.mongobase import user_collection
from Filters.Filtirlar import SubscriptionFilter

channels_collection = kanal['kanallar']
channel_vaqt = kanal['vaqtK']
user_requests = kanal['user_requests']
user_reques = kanal['user_req']
admins_collection = adminbase['adminlar']

rt = Router()

async def kanld(call: CallbackQuery):
    await call.message.edit_text("*Qaysi birisizga kerak ❓*", parse_mode="Markdown", reply_markup=kanalyesno)

# Umirlik kanal qo'shish boshlanishi
async def umr(call: CallbackQuery, state: FSMContext):
    await call.message.bot.send_message(chat_id=call.message.chat.id, text="Iltimos avval kanal nomini kriting")
    await state.set_state(Statelar.umr.umrk)

# Kanal nomini olish
async def umr1(message: Message, state: FSMContext):
    await state.update_data(nomi=message.text)
    await message.answer("Kanal nomi olindi, endi kanal userini yuboring (@ bilan boshlanadi)")
    await state.set_state(Statelar.umr.umrb)

# Kanal username va silka olish
async def umr4(message: Message, state: FSMContext):
    if not message.text.startswith('@'):
        return await message.answer("Iltimos kanal useri @ bilan boshlansin")

    await state.update_data(username=message.text)
    await message.answer("Endi kanal silkasini yuboring")
    await state.set_state(Statelar.umr.umrt)

# Kanalni DB ga qo'shish
async def umr2(message: Message, state: FSMContext):
    data = await state.get_data()

    user_data = {
        "channel_name": data['nomi'],
        "channel_type": "public",
        "channel_username": data['username'],
        "invite_link": message.text
    }

    channels_collection.insert_one(user_data)

    await message.answer("Kanal muvaffaqiyatli qo‘shildi ✅")
    await state.clear()

async def Kanal(call: CallbackQuery):
    await call.message.edit_text("*Nima qilmoqchisiz*", parse_mode="Markdown", reply_markup=kanaltugmasi)

async def ortga(call: CallbackQuery):
    await call.message.edit_text("*Qaysi birisizga kerak ❓*", parse_mode="Markdown", reply_markup=kanalyesno)

async def ortga1(call: CallbackQuery):
    await call.message.edit_text("*admin tugmalari marhamat nima qilmoqchisiz 📌✒*", parse_mode="Markdown", reply_markup=adminpaneltug)

async def get_admins() -> list[int]:
    """
    MongoDB dan admin user_id larini oladi
    """
    admins = admins_collection.find({})
    return [admin['user_id'] for admin in admins]


ijtimoiy_db = kanal["ijtimoiy_links"]

async def create_sub_keyboard(user_id: int, bot: Bot):

    docs = list(channels_collection.find({})) + list(channel_vaqt.find({})) + list(user_requests.find({}))

    kb = InlineKeyboardMarkup(inline_keyboard=[])

    # ====== TELEGRAM KANALLAR ======
    for doc in docs:

        name = doc.get("channel_name")
        channel_username = doc.get("channel_username")
        channel_type = doc.get("channel_type")
        invite_link = doc.get("invite_link")

        if not channel_username and channel_type != "private":
            continue

        if channel_type == "private":

            if not invite_link:
                continue

            url = invite_link

        else:

            username = channel_username.replace("@", "")
            url = f"https://t.me/{username}"

        try:
            if channel_username:
                status = await bot.get_chat_member(channel_username, user_id)

                if status.status in ["member", "administrator", "creator"]:
                    continue

        except:
            pass

        kb.inline_keyboard.append(
            [InlineKeyboardButton(text=name, url=url, style="danger")]
        )

    # ====== IJTIMOIY TARMOQLAR ======
    socials = list(ijtimoiy_db.find({}))

    for soc in socials:

        network = soc.get("network")
        link = soc.get("link")

        if not link:
            continue

        if network == "instagram":
            name = "Instagram"

        elif network == "facebook":
            name = "Facebook"

        elif network == "youtube":
            name = "Youtube"

        elif network == "discord":
            name = "Discord"

        else:
            continue

        kb.inline_keyboard.append(
            [InlineKeyboardButton(text=name, url=link)]
        )

    # ====== TEKSHIRISH ======
    kb.inline_keyboard.append(
        [InlineKeyboardButton(text="Tekshirish ✅", callback_data="check_subs", style='success')]
    )

    kb.inline_keyboard.append(
        [InlineKeyboardButton(text="Free💎", callback_data="Freevip", style="primary")]
    )

    return kb


async def send_welcome(message: Message, bot: Bot):
    user = message.from_user

    user_data = user_collection.find_one({"user_id": user.id})

    if not user_data:
        # yangi user qo‘shiladi (HAMMA FIELDLAR bilan)
        user_collection.insert_one({
            "user_id": user.id,
            "username": user.username,
            "full_name": user.full_name,

            "balance": 0,
            "referal": 0,
            "last_button_press": None,

            "joined_date": datetime.utcnow(),
            "last_active": datetime.utcnow()
        })
    else:
        # bor bo‘lsa yangilanadi
        user_collection.update_one(
            {"user_id": user.id},
            {
                "$set": {
                    "username": user.username,
                    "full_name": user.full_name,
                    "last_active": datetime.utcnow()
                }
            }
        )

    kb = await create_sub_keyboard(user.id, bot)

    await message.answer(
        "⚡ Iltimos, barcha kanallarga obuna bo‘ling: ⚠",
        reply_markup=kb
    )


async def check_subscriptions(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    all_ok = True
    missing_channels = []

    docs = list(channels_collection.find({})) + list(channel_vaqt.find({})) + list(user_requests.find({}))

    for doc in docs:
        channel_type = doc.get("channel_type")
        channel_username = doc.get("channel_username")
        channel_name = doc.get("channel_name")
        invite_link = doc.get("invite_link")

        # PUBLIC kanal
        if channel_type == "public":
            try:
                member = await bot.get_chat_member(channel_username, user_id)
                if member.status not in ["member", "administrator", "creator"]:
                    all_ok = False
                    missing_channels.append(channel_name)
            except:
                all_ok = False
                missing_channels.append(channel_name)

        # PRIVATE kanal
        elif channel_type == "private":
            user = user_reques.find_one({
                "user_id": user_id,
                "channel_name": channel_name
            })

            # Agar join request yuborilmagan
            if not user:
                all_ok = False
                missing_channels.append(channel_name)
            # Agar join request yuborilgan, ammo tasdiqlanmagan
            elif not user.get("approved", False):
                all_ok = False
                missing_channels.append(channel_name)

    if all_ok:
        await callback.message.answer("💚 Siz barcha kanallarga obuna bo‘ldingiz! <tg-emoji emoji-id='5372878077250519677'>✅</tg-emoji>", parse_mode="HTML")
    else:
        kb = await create_sub_keyboard(user_id, bot)
        msg = "❌ Siz hali hamma kanallarga obuna bo‘lmagansiz!\n"
        msg += "Obuna bo‘lishingiz kerak bo‘lgan kanallar:\n" + "\n".join(missing_channels)
        await callback.message.answer(msg, reply_markup=kb)


# Routerga register qilish
rt.callback_query.register(check_subscriptions, F.data == "check_subs")
rt.message.register(send_welcome, SubscriptionFilter())
rt.callback_query.register(kanld, F.data == "Kanali")
rt.callback_query.register(Kanal, F.data == "qoshdim")
rt.callback_query.register(ortga, F.data == "orqada")
rt.callback_query.register(ortga1, F.data == "orqadda")
rt.callback_query.register(umr, F.data == "umrkanal")
rt.message.register(umr1, Statelar.umr.umrk)
rt.message.register(umr4, Statelar.umr.umrb)
rt.message.register(umr2, Statelar.umr.umrt)

