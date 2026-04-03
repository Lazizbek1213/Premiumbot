from pymongo import MongoClient
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from Inlinebutton import adminpaneltug
rt = Router()


client = MongoClient("mongodb+srv://Lazizbek_1212L:Lazizbek_12@cluster0.cefy16t.mongodb.net/")
kanal = client["Kanal"]
adminbase = client['adminbotga']
admin_calleks = adminbase['adminlar']
channel_vaqt = kanal["vaqtK"]

Yuklashga = client['Contentga']
TrueFalse_Y = Yuklashga["TF"]

elonga = client['Elonga']
elon_collection = elonga["elonlar"]

user = client['Userlar']
user_collection = user["users"]

promokod = client['promokodlar']
promokod_collektion = promokod["promokod"]

qoshim = client['Qoshimcha']
subscribers_collection = qoshim["obuna"]
saved_collection = qoshim["saqlash"]
short_collection = qoshim["shorts"]
kanluchun = qoshim['postkanal']

premium = client["Free"]
Free_collecks = premium["Freeobunalar"]

kunlik = client["animekunda"]
kundalik_collection = kunlik["kundalikanime"]

anime_db = client['Anime']
anime_collection = anime_db["anime"]
qsmi_collection = anime_db["qsmi"]
Filim_collection = anime_db["Filim"]


# Obuna DB
saqlashi = client['saqlash']
obuna_colleks = saqlashi['obuna']


keyboard_collection = kanal["tugma"]
tili_collection = kanal["tili"]
ref_collection = kanal["referal"]
korishlar_collection = kanal["korishlar"]

pay_db = client["payment"]
cartas = pay_db["cartas"]


# Komment bazasi
komun = client["elon"]
komment_collection = komun["komment"]

remote_db = client['Post']
anime_collection12 = remote_db["kanal"]
qsim_collection12 = remote_db["content"]
kanluchunpost = remote_db["postkanal"]

def get_carta():
    return cartas.find_one()


def add_carta(number):
    cartas.delete_many({})  # eski kartani o‘chirish
    cartas.insert_one({"number": number})



if "expire_at_1" not in channel_vaqt.index_information():
    channel_vaqt.create_index("expire_at", expireAfterSeconds=0)
    print("TTL Indeks muvaffaqiyatli yaratildi!")


YUkla = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Yangilash♻", callback_data="statistik1")
        ],
        [
            InlineKeyboardButton(text="Ortga◀", callback_data="Ortga9")
        ]
    ]
)

@rt.callback_query(F.data == "Ortga9")
async def show_statistics(call: CallbackQuery):
    await call.message.edit_text("*admin tugmalari marhamat nima qilmoqchisiz 📌✒️*", parse_mode="Markdown", reply_markup=adminpaneltug)

@rt.callback_query(F.data == "statistik")
async def show_statistics(call: CallbackQuery):
    # Foydalanuvchilar soni
    user_count = user_collection.count_documents({})
    obuna_count = obuna_colleks.count_documents({})

    # Saqlanganlar va shortlar
    saved_count = saved_collection.count_documents({})
    short_count = short_collection.count_documents({})

    # Premium va Free obunalar
    free_count = Free_collecks.count_documents({})

    # Anime va qism soni
    anime_count = anime_collection.count_documents({})
    qsmi_count = qsmi_collection.count_documents({})

    # Elonlar va kommentlar
    elon_count = elon_collection.count_documents({})
    komment_count = komment_collection.count_documents({})

    # To‘lov kartalari mavjudligi
    carta = get_carta()
    carta_number = carta["number"] if carta else "❌ Yo‘q"

    # Telegram xabar matni
    stats_text = f"""
<blockquote>📊 <b>Bot Statistikasi</b></blockquote>

👥 <b>Foydalanuvchilar:</b> {user_count}
🔔 <b>Obunalar:</b> {obuna_count}

💾 <b>Saqlangan videolar:</b> {saved_count}
🎬 <b>Shortlar:</b> {short_count}

💎 <b>Free obunalar:</b> {free_count}

📺 <b>Anime soni:</b> {anime_count}
🎭 <b>Anime qismlari:</b> {qsmi_count}

📢 <b>Elonlar:</b> {elon_count}
💬 <b>Kommentlar:</b> {komment_count}

💳 <b>To‘lov kartasi:</b> {carta_number}

🚀 Statistika yangilanishi realtime
"""
    await call.message.edit_text(
        stats_text,
        parse_mode="HTML",
        reply_markup=YUkla
    )

@rt.callback_query(F.data == "statistik1")
async def show_statistics(call: CallbackQuery):
    # Foydalanuvchilar soni
    user_count = user_collection.count_documents({})
    obuna_count = obuna_colleks.count_documents({})

    # Saqlanganlar va shortlar
    saved_count = saved_collection.count_documents({})
    short_count = short_collection.count_documents({})

    # Premium va Free obunalar
    free_count = Free_collecks.count_documents({})

    # Anime va qism soni
    anime_count = anime_collection.count_documents({})
    qsmi_count = qsmi_collection.count_documents({})

    # Elonlar va kommentlar
    elon_count = elon_collection.count_documents({})
    komment_count = komment_collection.count_documents({})

    # To‘lov kartalari mavjudligi
    carta = get_carta()
    carta_number = carta["number"] if carta else "❌ Yo‘q"

    # Telegram xabar matni
    stats_text = f"""
<blockquote>📊 <b>Bot Statistikasi</b></blockquote>

👥 <b>Foydalanuvchilar:</b> {user_count}
🔔 <b>Obunalar:</b> {obuna_count}

💾 <b>Saqlangan videolar:</b> {saved_count}
🎬 <b>Shortlar:</b> {short_count}

💎 <b>Free obunalar:</b> {free_count}

📺 <b>Anime soni:</b> {anime_count}
🎭 <b>Anime qismlari:</b> {qsmi_count}

📢 <b>Elonlar:</b> {elon_count}
💬 <b>Kommentlar:</b> {komment_count}

💳 <b>To‘lov kartasi:</b> {carta_number}

🚀 Statistika Yangilandi✅
"""
    await call.message.edit_text(
        stats_text,
        parse_mode="HTML",
        reply_markup=YUkla
    )