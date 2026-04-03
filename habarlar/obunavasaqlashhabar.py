from aiogram import Router, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InputMediaPhoto, Message
from database.mongobase import saved_collection, anime_collection, subscribers_collection, admin_calleks
from Inlinebutton import nastroyka_menu
import math
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

rt = Router()
ITEMS_PER_PAGE = 6

# Inline tugmalar yaratish funksiyasi
def generate_saved_buttons(user_id: int, page: int = 0):
    saved_animes = list(saved_collection.find({"user_id": user_id}))
    total_pages = math.ceil(len(saved_animes) / ITEMS_PER_PAGE)
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE

    inline_keyboard = []

    # Anime tugmalari 🎥 bilan
    for anime in saved_animes[start:end]:
        inline_keyboard.append([InlineKeyboardButton(
            text=f"🎥 {anime['nomi']}", callback_data=f"saqlanganda_{anime['code']}"
        )])

    # Navigatsiya tugmalari
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="◀ Oldingi", callback_data=f"page_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="Keyingi ▶", callback_data=f"page_{page+1}"))
    if nav_buttons:
        inline_keyboard.append(nav_buttons)

    # Doimiy Tozalash tugmasi 🗑️
    inline_keyboard.append([InlineKeyboardButton(text="🗑️ Tozalash", callback_data="clear_saved")])
    inline_keyboard.append([InlineKeyboardButton(text="Ortga◀", callback_data="Ortga3")])

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
@rt.callback_query(F.data == "Ortga3")
async def Ortga(call: CallbackQuery):
    await call.message.edit_text(text="⚙️ Nastroyka menyusi", reply_markup=nastroyka_menu(2))

# Saqlangan animelarni ko'rsatish
@rt.callback_query(F.data == "saqlangan")
async def show_user_saved(call: CallbackQuery):
    kb = generate_saved_buttons(call.from_user.id, page=0)
    await call.message.edit_text("📚 Siz saqlagan animelar:", reply_markup=kb)

# Paginate tugmalar va Tozalash
@rt.callback_query(lambda c: c.data.startswith("page_") or c.data == "clear_saved")
async def navigate_or_clear(call: CallbackQuery):
    user_id = call.from_user.id
    if call.data.startswith("page_"):
        page = int(call.data.split("_")[1])
        kb = generate_saved_buttons(user_id, page)
        await call.message.edit_reply_markup(reply_markup=kb)
    elif call.data == "clear_saved":
        saved_collection.delete_many({"user_id": user_id})
        await call.message.edit_text("✅ Barcha saqlangan animelar tozalandi.", reply_markup=None)

# Har bir anime tugmasiga bosilganda batafsil ma'lumot
@rt.callback_query(lambda c: c.data.startswith("saqlanganda_"))
async def show_anime_detail(call: CallbackQuery):
    code = call.data.split("_")[1]
    anime = anime_collection.find_one({"code": code})
    if not anime:
        await call.message.answer("❌ Anime topilmadi.")
        return

    text = (
        f"🎬 <b>{anime['nomi']}</b>\n"
        f"📺 Qism: {anime.get('qismi', 'Nomalum')}\n"
        f"🎭 Janr: {anime.get('janr', 'Nomalum')}\n"
        f"🗣️ Til: {anime.get('tili', 'Nomalum')}\n"
        f"📆 Yili: {anime.get('yili', 'Nomalum')}"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬇️ Yuklash", callback_data=f"nomi_{anime['code']}")],
        [InlineKeyboardButton(text="saqlangandan ochirish💥", callback_data=f"salangan_ochir_{anime['code']}")]
    ])

    await call.message.edit_media(
        media=InputMediaPhoto(media=anime.get("photo"), caption=text, parse_mode="HTML"),
        reply_markup=kb
    )

@rt.callback_query(F.data.startswith("salangan_ochir_"))
async def remove_saved_anime(call: CallbackQuery):
    # callback_data: salangan_ochir_<anime_code>
    code = call.data.split("_")[-1]
    user_id = call.from_user.id

    # Faqat shu user va shu code ga mos saqlangan animeni o'chirish
    result = saved_collection.delete_one({"user_id": user_id, "code": code})

    if result.deleted_count > 0:
        await call.message.answer("✅ Anime saqlanganlardan o‘chirildi!")
        # Optional: tugmalar bilan ro'yxatni yangilash
        # kb = generate_saved_buttons(user_id, page=0)
        # await call.message.edit_text("📚 Siz saqlagan animelar:", reply_markup=kb)
    else:
        await call.message.answer("❌ Bu anime saqlanganlar orasida topilmadi.")


ITEMS_PER_PAGE1 = 6

# Obuna bo'limi tugmalar yaratish
def generate_subscription_buttons(user_id: int, page: int = 0):
    user_subs = list(subscribers_collection.find({"user_id": user_id}))
    total_pages = math.ceil(len(user_subs) / ITEMS_PER_PAGE1)
    start = page * ITEMS_PER_PAGE1
    end = start + ITEMS_PER_PAGE1

    inline_keyboard = []

    # Anime tugmalari 🎬
    for sub in user_subs[start:end]:
        inline_keyboard.append([InlineKeyboardButton(
            text=f"🎬 {sub['nomi']}", callback_data=f"sub_remove_{sub['code']}"
        )])

    # Navigatsiya tugmalari
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="◀ Oldingi", callback_data=f"sub_page_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="Keyingi ▶", callback_data=f"sub_page_{page+1}"))
    if nav_buttons:
        inline_keyboard.append(nav_buttons)

    # Doimiy Tozalash tugmasi 🗑️
    inline_keyboard.append([InlineKeyboardButton(text="🗑️ Tozalash", callback_data="sub_clear_all")])
    inline_keyboard.append([InlineKeyboardButton(text="Ortga◀", callback_data="Ortga4")])

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

# Obuna bo‘limini ko‘rsatish
@rt.callback_query(F.data == "obunalar")
async def show_user_subscriptions(call: CallbackQuery):
    kb = generate_subscription_buttons(call.from_user.id, page=0)
    await call.message.edit_text("📚 Siz obuna bo‘lgan animelar:", reply_markup=kb)

# Navigatsiya va Tozalash
@rt.callback_query(lambda c: c.data.startswith("sub_page_") or c.data == "sub_clear_all")
async def navigate_or_clear_subs(call: CallbackQuery):
    user_id = call.from_user.id
    if call.data.startswith("sub_page_"):
        page = int(call.data.split("_")[-1])
        kb = generate_subscription_buttons(user_id, page)
        await call.message.edit_reply_markup(reply_markup=kb)
    elif call.data == "sub_clear_all":
        subscribers_collection.delete_many({"user_id": user_id})
        await call.message.edit_text("✅ Barcha obuna bo‘lgan animelar tozalandi.", reply_markup=None)

# Faqat shu anime obunadan o'chirish
@rt.callback_query(F.data.startswith("sub_remove_"))
async def remove_subscription(call: CallbackQuery):
    code = call.data.split("_")[-1]
    user_id = call.from_user.id
    result = subscribers_collection.delete_one({"user_id": user_id, "code": code})

    if result.deleted_count > 0:
        await call.message.answer("✅ Bu anime obunalardan o‘chirildi!")
        kb = generate_subscription_buttons(user_id, page=0)
        await call.message.edit_text("📚 Siz obuna bo‘lgan animelar:", reply_markup=kb)
    else:
        await call.message.answer("❌ Bu anime obuna ro‘yxatida topilmadi.")

@rt.callback_query(F.data == "Ortga4")
async def Ortga(call: CallbackQuery):
    await call.message.edit_text(text="⚙️ Nastroyka menyusi", reply_markup=nastroyka_menu(2))


class AdminReply(StatesGroup):
    waiting_for_reply = State()
    waiting_for_media = State()


class AdminReply1(StatesGroup):
    waiting_for_reply1 = State()

@rt.callback_query(F.data == "adminjab")
async def adminsend(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("*adminga yubormoqchi bolgan habaringizni yuboring✅📍*", parse_mode="Markdown")
    await state.set_state(AdminReply1.waiting_for_reply1)

# Foydalanuvchi adminlarga xabar yuboradi
@rt.message(AdminReply1.waiting_for_reply1)
async def user_to_admin(message: Message, state: FSMContext):
    admin_ids = [a['user_id'] for a in admin_calleks.find()]

    for admin_id in admin_ids:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="↩️ Javob berish", callback_data=f"reply_{message.from_user.id}")]
        ])
        await message.bot.send_message(
            admin_id,
            text=f"*📩 Foydalanuvchidan xabar:\n\n{message.text}\n\nYubordi: {message.from_user.full_name} id: ( {message.from_user.id})*",
            reply_markup=kb,
            parse_mode="Markdown"
        )
    await message.answer("✅ Xabaringiz adminlarga yuborildi.")
    await state.clear()


# Admin reply tugmasini bosganda FSMni ishga tushiramiz
@rt.callback_query(F.data.startswith("reply_"))
async def admin_reply_prompt(call: CallbackQuery, state: FSMContext):
    user_id = int(call.data.replace("reply_", ""))
    await state.update_data(user_id=user_id)
    await call.message.edit_text("✏️ Javob matnini kiriting (yoki /skip - agar matn bo‘lmasa):")
    await state.set_state(AdminReply.waiting_for_reply)


# Matnni qabul qilish
@rt.message(AdminReply.waiting_for_reply)
async def admin_send_text(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']

    # /skip bilan matnsiz javob yuborish
    if message.text != "/skip":
        await message.bot.send_message(user_id, f"📩 Admindan javob:\n\n{message.text}")

    await message.answer("📎 Endi rasm yoki video yuboring, yoki /skip bilan o‘tish mumkin.")
    await state.set_state(AdminReply.waiting_for_media)


# Media (rasm/video) qabul qilish
@rt.message(AdminReply.waiting_for_media)
async def admin_send_media(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']

    if message.photo:
        file_id = message.photo[-1].file_id
        await message.bot.send_photo(user_id, photo=file_id, caption="📩 Admindan media")
    elif message.video:
        file_id = message.video.file_id
        await message.bot.send_video(user_id, video=file_id, caption="📩 Admindan media")

    await message.answer("✅ Javob foydalanuvchiga yuborildi.")
    await state.clear()