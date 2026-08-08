from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta, timezone
from database.mongobase import user_collection, Free_collecks, admin_calleks, promokod_collektion, channel_vaqt
import asyncio


rt = Router()

# =======================
# INLINE KEYBOARDS
# =======================
def free_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💳 Sotib olish", callback_data="buy_free", style='primary'),
                InlineKeyboardButton(text="📚 Qo'llanma", callback_data="guide_step1", style='success')
            ]
        ]
    )

def buy_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1️⃣ Oylik", callback_data="tarif_1"),
                InlineKeyboardButton(text="6️⃣ Oylik", callback_data="tarif_6"),
                InlineKeyboardButton(text="1️⃣ Yillik", callback_data="tarif_12")
            ],
            [
                InlineKeyboardButton(text="◀ Orqaga", callback_data="back_free")
            ]
        ]
    )

def guide_nav(prev_step: str = None, next_step: str = None) -> InlineKeyboardMarkup:
    row = []
    if prev_step:
        row.append(InlineKeyboardButton(text="◀", callback_data=prev_step))
    if next_step:
        row.append(InlineKeyboardButton(text="▶", callback_data=next_step))
    return InlineKeyboardMarkup(inline_keyboard=[row]) if row else None

# =======================
# TEXTS
# =======================
def free_text(bot_name: str) -> str:
    return f"""
✨ *FREE OBUNA*

Assalomu alaykum hurmatli *{bot_name}* foydalanuvchisi 🤝  

Bizni qo‘llab-quvvatlayotganingiz uchun katta rahmat! ❤️  

•🚀 Afzalliklar:
• ❌ Kanallarga obuna bo‘lish shart emas  
• 🤖 Botdan cheksiz foydalanish  
• 🔒 Pullik funksiyalarni ishlatish  
• 🎬 Pullik animelarni bepul ko‘rish  

"""

guide_texts = {
    "1": "📚 *QO'LLANMA - STEP 1*\n⚙️ *Nastroyka tugmasini bosing va Pul kiritish tugmasini tanlang✅.*",
    "2": "📚 *STEP 2*\nKerakli ma'lumotlarni to'ldiring va bot ko'rsatmalariga amal qiling 🤖",
    "3": "⚠️ *STEP 3*\n❗ Rasmlarni *bitta-bitta* yuboring\n❌ *ALBOM qilib yubormang*\n⚠ Ehtiyot bo'ling!\n`Agar hammasi to‘g‘ri bo‘lsa, 💰 hisobingiz to‘ldiriladi`",
    "4": "🎉 *STEP 4*\n💳 Obunaga sotib olish tugmasini bosing va o‘zingizga kerakli tarifni tanlang"
}

# =======================
# START HANDLER
# =======================
@rt.message(F.text == "Free⚠")
async def start(message: Message, state: FSMContext):
    bot_user = await message.bot.get_me()
    bot_name = bot_user.first_name or "Bot"
    await message.answer(free_text(bot_name), reply_markup=free_keyboard(), parse_mode="Markdown")

@rt.callback_query(F.data == "Freevip")
async def start(call: CallbackQuery, state: FSMContext):
    bot_user = await call.message.bot.get_me()
    bot_name = bot_user.first_name or "Bot"
    await call.message.edit_text(free_text(bot_name), reply_markup=free_keyboard(), parse_mode="Markdown")

# =======================
# CALLBACK HANDLERS
# =======================
# Qo'llanma steplari
for step in range(1, 5):
    async def guide_step_handler(call: CallbackQuery, state: FSMContext, step_num=step):
        text = guide_texts.get(str(step_num), "Step topilmadi")
        prev_step = f"guide_step{step_num-1}" if step_num > 1 else None
        next_step = f"guide_step{step_num+1}" if step_num < 4 else None
        await call.message.edit_text(text, reply_markup=guide_nav(prev_step, next_step), parse_mode="Markdown")
        await call.answer()
    rt.callback_query(F.data == f"guide_step{step}")(guide_step_handler)

# Sotib olish menu
@rt.callback_query(F.data == "buy_free")
async def buy_free_handler(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "*💳 Obuna sotib olish\nQuyidagi tariflardan birini tanlang 👇*\n *1-oylik💵: 5,000 so`m📌*\n *6-oylik💵: 27,000 so`m📌*\n *1-yillik💵: 60,000 so`m📌*",
        reply_markup=buy_keyboard(),
        parse_mode="Markdown"
    )
    await call.answer()


# Back tugma
@rt.callback_query(F.data == "back_free")
async def back_free_handler(call: CallbackQuery, state: FSMContext):
    bot_user = await call.bot.get_me()
    bot_name = bot_user.first_name or "Bot"
    await call.message.edit_text(free_text(bot_name), reply_markup=free_keyboard(), parse_mode="Markdown")
    await call.answer()

async def biroylik(call: CallbackQuery, bot: Bot):
    user_id = call.from_user.id
    user = user_collection.find_one({"user": user_id})

    if not user:
        await call.message.answer("Foydalanuvchi topilmadi")
        return

    price = 5000

    if user['balance'] < price:
        await call.message.answer("*Balans yetarli emas*", parse_mode="Markdown")
        return

    new_balance = user['balance'] - price
    user_collection.update_one({"user": user_id}, {"$set": {"balance": new_balance}})

    now = datetime.now(timezone.utc)

    sub = Free_collecks.find_one({"user_id": user_id})

    if sub and sub['expire_at'] > now:
        expire = sub['expire_at'] + timedelta(days=30)
    else:
        expire = now + timedelta(days=30)

    Free_collecks.update_one(
        {"user_id": user_id},
        {"$set": {"expire_at": expire}},
        upsert=True
    )

    await call.message.answer(
        f"✅ 1 oylik premium sotib olindi\n"
        f"💰 Yangi balans: {new_balance}\n"
        f"📅 Tugash vaqti: {expire.date()}"
    )

async def oltioylik(call: CallbackQuery, bot: Bot):
    user_id = call.from_user.id
    user = user_collection.find_one({"user": user_id})

    price = 20000

    if user['balance'] < price:
        await call.message.answer("*Balans yetarli emas*", parse_mode="Markdown")
        return

    new_balance = user['balance'] - price
    user_collection.update_one({"user": user_id}, {"$set": {"balance": new_balance}})

    now = datetime.now(timezone.utc)

    sub = Free_collecks.find_one({"user_id": user_id})

    if sub and sub['expire_at'] > now:
        expire = sub['expire_at'] + timedelta(days=180)
    else:
        expire = now + timedelta(days=180)

    Free_collecks.update_one(
        {"user_id": user_id},
        {"$set": {"expire_at": expire}},
        upsert=True
    )

    await call.message.answer(
        f"✅ 6 oylik premium sotib olindi\n"
        f"💰 Yangi balans: {new_balance}\n"
        f"📅 Tugash vaqti: {expire.date()}"
    )

async def Yillik(call: CallbackQuery, bot: Bot):
    user_id = call.from_user.id
    user = user_collection.find_one({"user": user_id})

    price = 50000

    if user['balance'] < price:
        await call.message.answer("*Balans yetarli emas*", parse_mode="Markdown")
        return

    new_balance = user['balance'] - price
    user_collection.update_one({"user": user_id}, {"$set": {"balance": new_balance}})

    now = datetime.now(timezone.utc)

    sub = Free_collecks.find_one({"user_id": user_id})

    if sub and sub['expire_at'] > now:
        expire = sub['expire_at'] + timedelta(days=365)
    else:
        expire = now + timedelta(days=365)

    Free_collecks.update_one(
        {"user_id": user_id},
        {"$set": {"expire_at": expire}},
        upsert=True
    )

    await call.message.answer(
        f"✅ 1 yillik premium sotib olindi\n"
        f"💰 Yangi balans: {new_balance}\n"
        f"📅 Tugash vaqti: {expire.date()}"
    )

Free_collecks.create_index("expire_at", expireAfterSeconds=0)

async def is_premium(user_id):
    sub = Free_collecks.find_one({"user_id": user_id})

    if not sub:
        return False

    if sub['expire_at'] > datetime.now(timezone.utc):
        return True

    return False



async def monitor_all(bot):
    while True:
        try:
            now = datetime.now(timezone.utc)

            # adminlarni olish
            admins = list(admin_calleks.find({}))
            admin_ids = [admin["user_id"] for admin in admins]

            # ---------------------------
            # 1️⃣ Kanal muddati tugashi
            # ---------------------------
            expired_channels = channel_vaqt.find({"expire_at": {"$lte": now}})
            for ch in expired_channels:
                for admin_id in admin_ids:
                    try:
                        await bot.send_message(
                            admin_id,
                            f"⏰ Kanal {ch['channel_name']} muddati tugadi"
                        )
                        await asyncio.sleep(0.3)
                    except Exception as e:
                        print(f"kanal xato: {e}")

                channel_vaqt.delete_one({"_id": ch["_id"]})

            # ---------------------------
            # 2️⃣ Premium tugashi
            # ---------------------------
            expired_users = Free_collecks.find({"expire_at": {"$lte": now}})
            for user in expired_users:
                try:
                    await bot.send_message(
                        user["user_id"],
                        "*❗ Sizning premium obunangiz tugadi. Agar yana olmoqchi bo'lsangiz pastdagi tugmani tanlang👇*",
                        parse_mode="Markdown",
                        reply_markup=buy_keyboard()
                    )
                    await asyncio.sleep(0.3)

                    Free_collecks.delete_one({"_id": user["_id"]})

                except Exception as e:
                    print(f"premium xato: {e}")

            # ---------------------------
            # 3️⃣ Promo kod muddati
            # ---------------------------
            expired_promos = promokod_collektion.find({"expire_at": {"$lte": now}})
            for promo in expired_promos:

                for admin_id in admin_ids:
                    try:
                        await bot.send_message(
                            admin_id,
                            f"⏰ Promo kod `{promo['code']}` muddati tugadi",
                            parse_mode="Markdown"
                        )
                        await asyncio.sleep(0.3)

                    except Exception as e:
                        print(f"promo xato: {e}")

                promokod_collektion.delete_one({"_id": promo["_id"]})

        except Exception as e:
            print(f"monitor_all umumiy xato: {e}")

        await asyncio.sleep(30)

@rt.message(F.text == "Anime buyurma🎭")
async def anime_buyurtma_handler(message: Message):
    text = (
        "🎭 *Anime buyurtma*\n\n"
        "📩 O‘zingiz xohlagan animeni buyurtma berish uchun admin bilan bog‘laning\n"
        "🚀 *Tezkor javob va sifatli xizmat*\n"
        "👤 Admin: @khaytbyv"
    )

    await message.answer(
        text=
        "🎭 <b>Anime buyurtma</b>\n\n"
        "📩 O‘zingiz xohlagan animeni buyurtma berish uchun admin bilan bog‘laning\n\n"
        "<blockquote>🚀 Tezkor javob va sifatli xizmat</blockquote>\n\n"
        "👤 Admin: @khaytbyv",
        parse_mode="HTML",
    )


rt.callback_query.register(biroylik, F.data == "tarif_1")
rt.callback_query.register(oltioylik, F.data == "tarif_6")
rt.callback_query.register(Yillik, F.data == "tarif_12")