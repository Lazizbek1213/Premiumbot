# file: post_module.py
from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.mongobase import anime_collection, qsmi_collection, anime_collection12, kanluchunpost
import Statelar
import html

rt = Router()

# ================== STATES ==================
class PostStates(StatesGroup):
    textpost = State()
    text = State()
    url = State()
    chanl = State()
    code = State()

class PhotoPostStates(StatesGroup):
    photo = State()
    text = State()
    code = State()
    chanl = State()
    url = State()

class VideoPostStates(StatesGroup):
    video = State()
    text = State()
    code = State()
    chanl = State()
    url = State()

class KanalPostStates(StatesGroup):
    post = State()

class DeletePostStates(StatesGroup):
    post = State()

class QsimPostStates(StatesGroup):
    codi = State()


@rt.callback_query(F.data == "Postkanal")
async def postlikanalde(call: CallbackQuery, state: FSMContext):
    tugma = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Kanal Qoshish➕", callback_data="Postkanal2")
            ],
            [
                InlineKeyboardButton(text="Kanal ochirish❌", callback_data="kanal_deletele")
            ]
        ]
    )
    await call.message.edit_text('*Nima qilmoqchisiz⁉*',reply_markup=tugma, parse_mode="Markdown")

# ================== KANAL QO‘SHISH BOSHLASH ==================
async def postkanal(call: CallbackQuery, state: FSMContext):
    await state.set_state(PostStates.textpost)
    await call.message.answer(
        "📢 *Kanal qo‘shish*\n\n"
        "*✍️ Kanal username yoki ID yuboring:*\n"
        "*Masalan:*\n"
        "*👉 @kanal_nomi*\n"
        "*👉 -1001234567890*",
        parse_mode="Markdown"
    )


# ================== KANAL SAQLASH ==================
async def postkanal1(message: Message, state: FSMContext):

    kanal = message.text.strip()

    # ❌ Bo‘sh tekshiruv
    if not kanal:
        await message.answer("❌ Iltimos, kanal username yoki ID kiriting!")
        return

    # ❌ Format tekshiruv (oddiy)
    if not (kanal.startswith("@") or kanal.startswith("-100")):
        await message.answer(
            "⚠️ Noto‘g‘ri format!\n\n"
            "To‘g‘ri misollar:\n"
            "👉 @kanal_nomi\n"
            "👉 -1001234567890"
        )
        return

    # ❌ Duplicate tekshiruv
    if kanluchunpost.find_one({"kanaluser": kanal}):
        await message.answer("⚠️ Bu kanal allaqachon qo‘shilgan!")
        return

    # ✅ Saqlash
    kanluchunpost.insert_one({"kanaluser": kanal})

    # 📋 Barcha kanallarni chiqarish
    channels = list(kanluchunpost.find({}))

    buttons = []
    for k in channels:
        buttons.append([
            InlineKeyboardButton(
                text=f"📤 {k['kanaluser']} ",
                callback_data=f"bob_{k['kanaluser']}"
            )
        ])

    # ➕ Qo‘shimcha tugmalar
    buttons.append([
        InlineKeyboardButton(text="➕ Yana kanal qo‘shish", callback_data="Postkanal")
    ])
    buttons.append([
        InlineKeyboardButton(text="❌ Kanalni o‘chirish", callback_data="kanal_deletele")
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer(
        "✅ *Kanal muvaffaqiyatli qo‘shildi!*\n\n"
        "📋 Mavjud kanallar:",
        parse_mode="Markdown",
        reply_markup=kb
    )

    await state.clear()

# ================== KANAL O‘CHIRISH ==================
@rt.callback_query(F.data == "kanal_deletele")
async def kanal_delete(call: CallbackQuery):

    channels = list(kanluchunpost.find({}))

    if not channels:
        await call.message.answer("❌ Hech qanday kanal yo‘q")
        return

    buttons = []
    for k in channels:
        buttons.append([
            InlineKeyboardButton(
                text=f"❌ {k['kanaluser']}",
                callback_data=f"delili_{k['kanaluser']}"
            )
        ])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await call.message.answer("🗑 O‘chirish uchun kanalni tanlang:", reply_markup=kb)


@rt.callback_query(F.data.startswith("delili_"))
async def kanal_delete_confirm(call: CallbackQuery):

    kanal = call.data.split("_")[1]

    kanluchunpost.delete_one({"kanaluser": kanal})

    await call.message.edit_text(f"✅ {kanal} o‘chirildi!")

# ================== ADMIN: POST QISMI ==================
async def qsimliku(call: CallbackQuery, state: FSMContext):
    await call.message.answer(
        "✏️ Postni kodi va qismini yuboring (namuna: 5=1)\n"
        "👉 Format: anime kodi = qismi"
    )
    await state.set_state(QsimPostStates.codi)


# 2. Qismni qabul qilish
async def qsimpost(message: Message, state: FSMContext):
    try:
        if not message.text or "=" not in message.text:
            return await message.reply("⚠️ Format noto‘g‘ri! Namuna: 5=1")

        code, qism = map(str.strip, message.text.split("=", 1))

        anime_data = anime_collection.find_one({"code": code})
        if not anime_data:
            return await message.reply("❌ Kod topilmadi!")

        name = anime_data.get("nomi", "Noma’lum")

        await state.update_data(code=code, qism=qism, name=name)

        buttons = []
        for k in kanluchunpost.find({}):
            kanal = k.get("kanaluser")
            if kanal:
                buttons.append([
                    InlineKeyboardButton(
                        text=f"{kanal} ga yuborish",
                        callback_data=f"ch={kanal}"
                    )
                ])

        buttons.append([InlineKeyboardButton(text="📢 Kanal", callback_data="kanalnips")])
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)

        # 🔥 HTML + escape (ENG TO‘G‘RI)
        caption = (
            f"📋 <b>Nomi:</b> {html.escape(str(name))}\n"
            f"🎞 <b>Qismi:</b> {html.escape(str(qism))}\n"
            f"🔣 <b>Code:</b> {html.escape(str(anime_data.get('code','')))}\n"
            f"🔠 <b>Tili:</b> {html.escape(str(anime_data.get('tili','')))}\n"
            f"🕑 <b>Yili:</b> {html.escape(str(anime_data.get('yili','')))}\n"
            f"🎭 <b>Janr:</b> {html.escape(str(anime_data.get('janr','')))}"
        )

        await message.answer_photo(
            photo=anime_data["photo"],
            caption=caption,
            parse_mode="HTML",
            reply_markup=kb
        )

    except Exception as e:
        await message.reply(f"❌ Xatolik: {e}")


# 3. Kanalga yuborish
@rt.callback_query(F.data.startswith("ch="))
async def postqsim(call: CallbackQuery, state: FSMContext):
    try:
        kanal = call.data.split("=", 1)[1]

        info = await state.get_data()
        code = info.get("code")
        qism = info.get("qism")
        name = info.get("name")

        if not all([code, qism, name]):
            return await call.answer("❌ Ma'lumot topilmadi!", show_alert=True)

        botga = await call.bot.get_me()

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Yuklash💚",
                        url=f"https://t.me/{botga.username}?start=post_{code}_{qism}"
                    )
                ]
            ]
        )

        await call.bot.send_message(
            chat_id=kanal,
            text=f"{name} - Qism {qism}",
            reply_markup=kb
        )

        await call.answer("✅ Kanalga yuborildi!")
        await state.clear()

    except Exception as e:
        await call.answer(f"❌ Xatolik: {e}", show_alert=True)

# ================== ADMIN: YUKLASH (TEXT, PHOTO, VIDEO) ==================
async def post1(call: CallbackQuery, state: FSMContext):
    await call.message.answer("✍️ Post nomini kiriting:")
    await state.set_state(PostStates.textpost)

async def nomi(message: Message, state: FSMContext):
    await state.update_data(nomi=message.text)
    await message.answer("✅ Nom olindi, endi post rasmini, videosi yoki textini yuboring")
    await state.set_state(PostStates.text)

async def videorasim(message: Message, state: FSMContext):
    if message.photo:
        photo = message.photo[-1].file_id
        await state.update_data(photo=photo)
        await message.answer("✅ Rasim olindi, izoh kiriting")
        await state.set_state(PhotoPostStates.text)
    elif message.video:
        video = message.video.file_id
        await state.update_data(video=video)
        await message.answer("✅ Video olindi, izoh kiriting")
        await state.set_state(VideoPostStates.text)
    elif message.text:
        await state.update_data(text=message.text)
        await message.answer("✅ Text olindi, endi tugma nomini kiriting")
        await state.set_state(PostStates.url)

async def text2(message: Message, state: FSMContext):
    await state.update_data(url=message.text)
    await message.answer("📌 URL olindi, endi kanal userini kiriting")
    await state.set_state(PostStates.chanl)

async def yuklash2(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    required_keys = ['nomi', 'text', 'url', 'code', 'video', 'photo']
    if not any(data.get(k) for k in required_keys):
        await message.answer("⚠️ Ba'zi ma'lumotlar yetishmayapti. Qayta urinib ko‘ring!")
        return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=data.get('nomi'), url=data.get('url'))]]
    )
    anime_collection12.insert_one(data)

    chat_id = message.text
    if data.get('video'):
        await bot.send_video(chat_id=chat_id, video=data['video'], caption=data.get('text'), reply_markup=kb)
    elif data.get('photo'):
        await bot.send_photo(chat_id=chat_id, photo=data['photo'], caption=data.get('text'), reply_markup=kb)
    else:
        await bot.send_message(chat_id=chat_id, text=data.get('text'), reply_markup=kb)

    await message.answer("✅ Yuklash yakunlandi, post kanalga yuborildi")
    await state.clear()

# ❌ Post o'chirish uchun
async def ochirish(call: CallbackQuery, state: FSMContext):
    tugma = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1 Talab❌", callback_data="1dan"),
                InlineKeyboardButton(text="Hammasini❌", callback_data='hamda')
            ]
        ]
    )
    await call.message.answer("Qaysi usulda postlarni o‘chirmoqchisiz?", reply_markup=tugma)

async def ochirish1(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("ochirmoqchi bolgan post codingizni yuboring")
    await state.set_state(Statelar.Postniyoqotish.ochirish)

# ❌ Faqat bitta postni code bo'yicha o'chirish
async def ochirish2(message: Message, state: FSMContext):
    result = anime_collection12.find_one({'code': message.text})
    if not result:
        await message.answer("❌ Bunday kodli post topilmadi!")
        return
    anime_collection12.delete_one({'code': message.text})
    await message.answer(f"✅ Post '{message.text}' o‘chirildi!")
    await state.clear()

# ❌ Barcha postlarni o'chirish
async def hamma(call: CallbackQuery, state: FSMContext):
    anime_collection12.delete_many({})
    await call.message.answer("✅ Barcha postlar o‘chirildi!", parse_mode="Markdown")

@rt.callback_query(F.data == "Post")
async def tugmalar(call: CallbackQuery):
    results = anime_collection12.find()  # Bir nechta hujjatlarni olish

    buttons = [
        [InlineKeyboardButton(
            text=result['nomi'],
            callback_data=f"postlarim_{result['code']}"
        )]
        for result in results
    ]

    buttons.append([
        InlineKeyboardButton(text="post qoshish💌", callback_data="postqosh")
    ])
    buttons.append([
        InlineKeyboardButton(text="Ochirish❌", callback_data="posoch")
    ])
    buttons.append([
        InlineKeyboardButton(text="qsim post💚", callback_data="qasim")
    ])
    buttons.append([
        InlineKeyboardButton(text="Ortga◀", callback_data="Ortga2")
    ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await call.message.edit_text(
        text="*nima qilmoqchisiz ?*",
        parse_mode="Markdown",
        reply_markup=keyboard
    )



# ================== REGISTER HANDLERS ==================
rt.callback_query.register(postkanal, F.data == 'Postkanal2')
rt.message.register(postkanal1, PostStates.textpost)
rt.callback_query.register(post1, F.data == "postqosh")
rt.message.register(nomi, PostStates.textpost)
rt.message.register(videorasim, PostStates.text)
rt.message.register(text2, PostStates.chanl)
rt.message.register(yuklash2, PostStates.url)
rt.callback_query.register(qsimliku, F.data == "qasim")
rt.message.register(qsimpost, QsimPostStates.codi)
rt.callback_query.register(ochirish, F.data == "posoch")
rt.callback_query.register(ochirish1, F.data == "1dan") # O'chirish tugmasi bosilganda
rt.callback_query.register(hamma, F.data == "hamda")       # Hammasini o'chirish
rt.callback_query.register(ochirish2, Statelar.Postniyoqotish.ochirish)      # Code bo'yicha o'chirish