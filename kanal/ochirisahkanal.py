from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from database.mongobase import kanal
from Inlinebutton import kanalyesno, orqada

rt = Router()

# MongoDB collections
channels_collection = kanal["kanallar"]      # ommaviy kanal
user_requests = kanal["user_requests"]       # maxfiy kanal
ijtimoiy_db = kanal["ijtimoiy_links"]        # ijtimoiy tarmoqlar


# ===== O'CHIRISH MENYU =====
ochirish_tugma = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Ommaviy kanal", callback_data="del_public"),
            InlineKeyboardButton(text="Maxfiy kanal", callback_data="del_private")
        ],
        [
            InlineKeyboardButton(text="Ijtimoiy tarmoq", callback_data="del_social"),
            InlineKeyboardButton(text="Ortga◀", callback_data="orqadali")
        ]
    ]
)


@rt.callback_query(F.data == "orqadali")
async def ortga(call: CallbackQuery):
    await call.message.edit_text("*Qaysi birisizga kerak ❓*", parse_mode="Markdown", reply_markup=kanalyesno)

@rt.callback_query(F.data == "ochirdim")
async def ochir1(call: CallbackQuery):
    await call.message.edit_text("*Qaysi turda Ochirmoqchisiz ❓*", parse_mode="Markdown", reply_markup=ochirish_tugma)

@rt.callback_query(F.data == "oldinor")
async def ochir1(call: CallbackQuery):
    await call.message.edit_text("*Qaysi turda Ochirmoqchisiz ❓*", parse_mode="Markdown", reply_markup=ochirish_tugma)

# ===== OMMAVIY KANAL RO'YXATI =====
@rt.callback_query(F.data == "del_public")
async def delete_public(call: CallbackQuery):

    docs = channels_collection.find({})
    kb = InlineKeyboardMarkup(inline_keyboard=[])

    for doc in docs:
        name = doc.get("channel_name")

        kb.inline_keyboard.append(
            [InlineKeyboardButton(text=name, callback_data=f"delpub_{name}")]
        )

    await call.message.edit_text("O‘chiriladigan kanalni tanlang", reply_markup=kb)


# ===== OMMAVIY KANAL O'CHIRISH =====
@rt.callback_query(F.data.startswith("delpub_"))
async def delete_public_channel(call: CallbackQuery):

    name = call.data.replace("delpub_", "")

    channels_collection.delete_one({"channel_name": name})

    await call.message.edit_text("✅ Ommaviy kanal o‘chirildi", reply_markup=orqada)


# ===== MAXFIY KANAL RO'YXATI =====
@rt.callback_query(F.data == "del_private")
async def delete_private(call: CallbackQuery):

    docs = user_requests.find({})
    kb = InlineKeyboardMarkup(inline_keyboard=[])

    for doc in docs:
        name = doc.get("channel_name")

        kb.inline_keyboard.append(
            [InlineKeyboardButton(text=name, callback_data=f"delpri_{name}")]
        )

    await call.message.edit_text("O‘chiriladigan maxfiy kanalni tanlang", reply_markup=kb)


# ===== MAXFIY KANAL O'CHIRISH =====
@rt.callback_query(F.data.startswith("delpri_"))
async def delete_private_channel(call: CallbackQuery):

    name = call.data.replace("delpri_", "")

    user_requests.delete_one({"channel_name": name})

    await call.message.edit_text("✅ Maxfiy kanal o‘chirildi", reply_markup=orqada)


# ===== IJTIMOIY TARMOQLAR RO'YXATI =====
@rt.callback_query(F.data == "del_social")
async def delete_social(call: CallbackQuery):

    docs = ijtimoiy_db.find({})
    kb = InlineKeyboardMarkup(inline_keyboard=[])

    for doc in docs:

        network = doc.get("network")

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
            [InlineKeyboardButton(text=name, callback_data=f"delsoc_{network}")]
        )

    await call.message.edit_text("O‘chiriladigan ijtimoiy tarmoqni tanlang", reply_markup=kb)


# ===== IJTIMOIY TARMOQ O'CHIRISH =====
@rt.callback_query(F.data.startswith("delsoc_"))
async def delete_social_network(call: CallbackQuery):

    network = call.data.replace("delsoc_", "")

    ijtimoiy_db.delete_one({"network": network})

    await call.message.edit_text("✅ Ijtimoiy tarmoq o‘chirildi", reply_markup=orqada)