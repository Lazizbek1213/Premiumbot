from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from database.mongobase import anime_collection, qsmi_collection
from Inlinebutton import adminpaneltug
import Statelar
import aiohttp

IMGBB_API_KEY = "4a7b2dbf39ce44ec8910b0d503dc6b11"

rt = Router()

Yuklashda = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Yuklash📥", callback_data="Yuklada"),
            InlineKeyboardButton(text="Ochirish📤", callback_data="Ochirbek")
        ],
        [
            InlineKeyboardButton(text="Yangilash🔄", callback_data="Yangilash")
        ],
        [
            InlineKeyboardButton(text="Ortga◀", callback_data="ortgachil")
        ]
    ]
)

@rt.callback_query(F.data == "Animeyuklashga")
async def yuklashda_animeli(call: CallbackQuery):
    await call.message.edit_text(
        "*Nima qilmoqchisiz ⁉*",
        parse_mode="Markdown",
        reply_markup=Yuklashda
    )

@rt.callback_query(F.data == "ortgachil")
async def yuklashda(call: CallbackQuery):
    await call.message.edit_text("*admin tugmalari marhamat nima qilmoqchisiz 📌✒️ ⁉*", parse_mode="Markdown", reply_markup=adminpaneltug)


# 1️⃣ Boshlash
@rt.callback_query(F.data == "Yuklada")
async def boshlash(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Iltimos, boshlanish uchun rasm yuboring.")
    await state.set_state(Statelar.Yuklash.photo)

# 2️⃣ Rasmni qabul qilish va IMGBB ga yuklash
@rt.message(Statelar.Yuklash.photo)
async def photo(message: Message, state: FSMContext, bot: Bot):
    if not message.photo:
        await message.answer("Faqat rasm yubor")
        return

    photo_file = message.photo[-1]
    file = await bot.get_file(photo_file.file_id)
    file_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"

    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as resp:
            image_data = await resp.read()

        form = aiohttp.FormData()
        form.add_field("key", IMGBB_API_KEY)
        form.add_field("image", image_data)

        async with session.post("https://api.imgbb.com/1/upload", data=form) as resp:
            data = await resp.json()
            imgbb_url = data["data"]["url"]

    await state.update_data(photo=imgbb_url)

    # 🔥 FARQI: video optional bo‘ladi
    await message.answer("✅ Rasm saqlandi.\nAgar video bo‘lsa yuboring, bo‘lmasa /skip yozing")
    await state.set_state(Statelar.Yuklash.video_optional)

@rt.message(Statelar.Yuklash.video_optional)
async def optional_video(message: Message, state: FSMContext):
    if message.text == "/skip":
        await state.update_data(main_video=None)
    elif message.video:
        await state.update_data(main_video=message.video.file_id)
    else:
        await message.answer("Video yubor yoki /skip yoz")
        return

    await message.answer("Endi qism sonini kiriting:")
    await state.set_state(Statelar.Yuklash.soni)

# 3️⃣ Qism soni
@rt.message(Statelar.Yuklash.soni)
async def soni(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(soni=int(message.text))
        await message.answer("Qism soni qabul qilindi. Endi nomini kiriting.")
        await state.set_state(Statelar.Yuklash.qsmi)
    else:
        await message.answer("Qism soni faqat raqam bo‘lishi kerak.")

# 4️⃣ Nom
@rt.message(Statelar.Yuklash.qsmi)
async def qsmi(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Nom qabul qilindi. Endi janrini kiriting (# bilan boshlang).")
    await state.set_state(Statelar.Yuklash.janr)

# 5️⃣ Janr
@rt.message(Statelar.Yuklash.janr)
async def janr(message: Message, state: FSMContext):
    if message.text.startswith("#"):
        await state.update_data(janr=message.text)
        await message.answer("Janr qabul qilindi. Endi tilini kiriting.")
        await state.set_state(Statelar.Yuklash.tili)
    else:
        await message.answer("Janrni # bilan boshlang.")

# 6️⃣ Til
@rt.message(Statelar.Yuklash.tili)
async def tili(message: Message, state: FSMContext):
    await state.update_data(tili=message.text)
    await message.answer("Til qabul qilindi. Endi chiqarilgan yilni kiriting.")
    await state.set_state(Statelar.Yuklash.yili)

# 7️⃣ Yil
@rt.message(Statelar.Yuklash.yili)
async def yili(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(yili=int(message.text))
        await message.answer("Yil qabul qilindi. Endi kodni kiriting.")
        await state.set_state(Statelar.Yuklash.kod)
    else:
        await message.answer("Yil faqat raqam bo‘lishi kerak.")

# 8️⃣ Kod
@rt.message(Statelar.Yuklash.kod)
async def code(message: Message, state: FSMContext):
    await state.update_data(code=message.text)
    data = await state.get_data()
    anime_collection.insert_one({
        "nomi": data.get('name'),
        "qismi": data.get('soni'),
        "janr": data.get('janr'),
        "tili": data.get('tili'),
        "yili": data.get('yili'),
        "code": data.get('code'),
        "photo": data.get('photo')
    })
    await message.answer("Kod qabul qilindi. Endi qismlarni ketma-ket yuklang.")
    await state.set_state(Statelar.Yuklash.video)

# 9️⃣ Video qabul qilish
@rt.message(Statelar.Yuklash.video)
async def video(message: Message, state: FSMContext):
    if message.video:
        data = await state.get_data()
        qsimi = data.get('qsimi', 0) + 1
        await state.update_data(qsimi=qsimi)

        qsmi_collection.insert_one({
            "qsimi": qsimi,
            "code": data.get('code'),
            "url": message.video.file_id,
            "caption": f"""🏷Anime nomi: {data.get('name')}
📽Qismlar soni: {data.get('soni')}
🖋Janri: {data.get('janr')}
💬Tili: {data.get('tili')}
🕑Yili: {data.get('yili')}"""
        })

        if qsimi < int(data.get('soni')):
            await message.answer(f"Video qabul qilindi. Qism {qsimi}/{data.get('soni')}. Keyingi qismini yuboring.")
        else:
            await message.answer("Hamma qismlar yuklandi. Kanal username yoki ID yuboring.")
            await state.set_state(Statelar.Yuklash.Yuklash)
    else:
        await message.answer("Faqat video yuboring.")

@rt.message(Statelar.Yuklash.Yuklash)
async def send_to_channel(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    channel_id = message.text
    botuser = await bot.get_me()

    caption = f"""🏷Anime nomi: {data.get('name')}
📽Qismlar soni: {data.get('soni')}
🖋Janri: {data.get('janr')}
💬Tili: {data.get('tili')}
🕑Yili: {data.get('yili')}"""

    tomosha = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Yuklash📥", url=f"https://t.me/{botuser.username}?start=anime_{data.get('code')}")]
        ]
    )

    # 🔥 LOGIKA
    if data.get("main_video"):
        # VIDEO POST
        await bot.send_video(
            chat_id=channel_id,
            video=data.get("main_video"),
            caption=caption,
            reply_markup=tomosha
        )
    else:
        # RASM POST
        await bot.send_photo(
            chat_id=channel_id,
            photo=data.get("photo"),
            caption=caption,
            reply_markup=tomosha
        )

    await message.answer("✅ Kanalga yuborildi")
    await state.clear()

OchirishTugma = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Anime o'chirish➖", callback_data="delete_anime"),
            InlineKeyboardButton(text="Qism o'chirish➖", callback_data="delete_qism")
        ],
        [
            InlineKeyboardButton(text="Ortga◀", callback_data="Ortga8")
        ]
    ]
)

PostTugma = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Rasm➕", callback_data="post_photo"),
            InlineKeyboardButton(text="Video➕", callback_data="post_video")
        ],
        [
            InlineKeyboardButton(text="Yoq❌", callback_data="no")
        ]
    ]
)

@rt.callback_query(F.data == "Ortga8")
async def yuklashda(call: CallbackQuery):
    await call.message.edit_text("*Nima qilmoqchisiz ⁉*", parse_mode="Markdown", reply_markup=Yuklashda)


# 🔹 Ochirish vaqti
@rt.callback_query(F.data == "Ochirbek")
async def ochirish(call: CallbackQuery):
    await call.message.edit_text("Nima o'chiriladi?", reply_markup=OchirishTugma)

@rt.callback_query(F.data == "delete_qism")
async def delete_qism(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Qaysi animeni qismi o'chiriladi? Kodni kiriting:")
    await state.set_state(Statelar.Ochirsh.qod)

@rt.message(Statelar.Ochirsh.qod)
async def get_qism_code(message: Message, state: FSMContext):
    code = message.text
    anime = anime_collection.find_one({"code": code})
    if anime:
        await state.update_data(code=code)
        await message.answer(f"Nechi qismni o'chirmoqchisiz? Maks {anime.get('qismi')}:")
        await state.set_state(Statelar.Ochirsh.qsmi)
    else:
        await message.answer("Bunday kod topilmadi!")

@rt.message(Statelar.Ochirsh.qsmi)
async def delete_qism_final(message: Message, state: FSMContext):
    qsmi = int(message.text)
    data = await state.get_data()
    code = data.get('code')

    qsmi_collection.delete_one({"code": code, "qsimi": qsmi})
    await message.answer(f"✅ Qism {qsmi} o'chirildi")
    await state.clear()

@rt.callback_query(F.data == "delete_anime")
async def delete_anime_final(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Qaysi animeni o'chirmoqchisiz? Kodni kiriting:")
    await state.set_state(Statelar.Ochirsh.anime_code)

@rt.message(Statelar.Ochirsh.anime_code)
async def delete_anime(message: Message, state: FSMContext):
    code = message.text
    anime_collection.delete_one({"code": code})
    qsmi_collection.delete_many({"code": code})
    await message.answer(f"✅ Anime va barcha qismlari o'chirildi!")
    await state.clear()


# ------------------ YANGILASH TUGMASI ------------------
@rt.callback_query(F.data == "Yangilash")
async def update_start(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Qaysi animeni qismini yangilamoqchisiz? Anime kodini kiriting:")
    await state.set_state(Statelar.UpdateAnime.code)

# ------------------ KOD SORASH ------------------
@rt.message(Statelar.UpdateAnime.code)
async def get_anime_code(message: Message, state: FSMContext):
    anime = anime_collection.find_one({"code": message.text})
    if not anime:
        await message.answer("❌ Bunday kod topilmadi!")
        return
    await state.update_data(anime_code=message.text)
    await message.answer(f"*{anime.get('nomi')}* anime uchun qancha qism video qo‘shmoqchisiz?", parse_mode="Markdown")
    await state.set_state(Statelar.UpdateAnime.qsmi_count)

# ------------------ QISM SONI SORASH ------------------
@rt.message(Statelar.UpdateAnime.qsmi_count)
async def get_qsmi_count(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam kiriting!")
        return
    await state.update_data(qsmi_count=int(message.text), uploaded_count=0)
    await message.answer("Endi videolarni ketma-ket yuboring:")
    await state.set_state(Statelar.UpdateAnime.inln)

@rt.message(Statelar.UpdateAnime.inln)
async def upload_video(message: Message, state: FSMContext):
    if not message.video:
        await message.answer("❌ Faqat video yubor")
        return

    data = await state.get_data()
    code = data.get("anime_code")

    # 🔥 TO‘G‘RI VARIANT
    last_doc = qsmi_collection.find_one(
        {"code": code},
        sort=[("qsimi", -1)]
    )

    last_qism = last_doc["qsimi"] if last_doc else 0
    new_qism = last_qism + 1

    anime = anime_collection.find_one({"code": code})

    qsmi_collection.insert_one({
        "code": code,
        "qsimi": new_qism,
        "url": message.video.file_id,
        "caption": f"""🏷Anime: {anime.get('nomi')}
📽Qism: {new_qism}
🖋Janr: {anime.get('janr')}
💬Til: {anime.get('tili')}
🕑Yil: {anime.get('yili')}"""
    })

    uploaded = data.get("uploaded", 0) + 1
    await state.update_data(uploaded=uploaded)

    if uploaded < data.get("qsmi_count"):
        await message.answer(f"Qabul qilindi {uploaded}/{data.get('qsmi_count')}")
    else:
        await message.answer("✅ Hamma qism yuklandi\nPost qilasizmi?", reply_markup=PostTugma)
        await state.set_state(Statelar.UpdateAnime.post_choice)

# ------------------ VIDEO YUKLASH ------------------
# ------------------ POST TANLASH ------------------
@rt.callback_query(F.data.startswith("post_"))
async def post_choice(call: CallbackQuery, state: FSMContext):
    choice = call.data.split("_")[1]
    await state.update_data(post_choice=choice)

    if choice == "no":
        await call.message.answer("Post qilinmaydi. Faqat ma'lumotlar yangilandi ✅")
        await state.clear()
        return

    if choice == "video":
        await call.message.answer("📹 1 ta video yuboring:")
        await state.set_state(Statelar.UpdateAnime.upload_video)

    elif choice == "photo":
        await call.message.answer("🖼 Rasm yuboring:")
        await state.set_state(Statelar.UpdateAnime.upload_photo)


# ------------------ VIDEO POST UCHUN (1 TA) ------------------
@rt.message(Statelar.UpdateAnime.upload_video)
async def upload_video_post(message: Message, state: FSMContext):
    if not message.video:
        await message.answer("❌ Faqat video yuboring.")
        return

    data = await state.get_data()

    if data.get("uploaded_video"):
        await message.answer("❌ Siz allaqachon video yuborgansiz.")
        return

    await state.update_data(uploaded_video=message.video.file_id)
    await message.answer("✅ Video qabul qilindi. Kanal username yoki ID yuboring:")
    await state.set_state(Statelar.UpdateAnime.channel)


# ------------------ RASM POST UCHUN ------------------
@rt.message(Statelar.UpdateAnime.upload_photo)
async def upload_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("❌ Faqat rasm yuboring.")
        return

    await state.update_data(uploaded_photo=message.photo[-1].file_id)
    await message.answer("✅ Rasm qabul qilindi. Kanal username yoki ID yuboring:")
    await state.set_state(Statelar.UpdateAnime.channel)


# ------------------ KANALGA POST ------------------
@rt.message(Statelar.UpdateAnime.channel)
async def post_to_channel(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()


    code = data.get('anime_code')
    channel_id = message.text
    post_choice = data.get('post_choice')

    qsmi_list = list(qsmi_collection.find({"code": code}).sort("qsimi", 1))

    total = qsmi_collection.count_documents({"code": code})

    anime_collection.update_one(
        {"code": code},
        {"$set": {"qismi": total}}
    )

    botuser = await bot.get_me()

    anime = anime_collection.find_one({"code": code})

    YUklash = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Yuklash", url=f"https://t.me/{botuser.username}?start=anime_{code}", style="primary")
            ]
        ]
    )

    # 🔹 RASM POST
    if post_choice == "photo":
        await bot.send_photo(
            chat_id=channel_id,
            photo=data.get("uploaded_photo"),
            reply_markup=YUklash,# USER yuborgan rasm
            caption=f"""🏷Anime nomi: {anime.get('nomi')}
📽Qismlar soni: {anime.get('qismi')}
🖋Janri: {anime.get('janr','-')}
💬Tili: {anime.get('tili','-')}
🕑Yili: {anime.get('yili','-')}"""
        )

    # 🔹 VIDEO POST (faqat 1 ta)
    elif post_choice == "video":
        await bot.send_video(
            chat_id=channel_id,
            reply_markup=YUklash,
            video=data.get("uploaded_video"),  # USER yuborgan video
            caption=f"""🏷Anime nomi: {anime.get('nomi')}
📽Qismlar soni: {anime.get('qismi')}
🖋Janri: {anime.get('janr','-')}
💬Tili: {anime.get('tili','-')}
🕑Yili: {anime.get('yili','-')}"""
        )

    await message.answer("✅ Post qilindi.")
    await state.clear()

