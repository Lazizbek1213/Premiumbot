from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup,KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def generate_inline_buttons(users, start_index=0):
    builder = InlineKeyboardBuilder()  # Tugmalarni yaratish uchun builder
    end_index = int(start_index) + 10

    for i in range(int(start_index), min(end_index, len(users))):
        user = users[i]
        builder.add(
            InlineKeyboardButton(
                text=f"{i + 1}",
                callback_data=f"anime_{user['code']}_{user['qsimi']}"
            )
        )

    # "Oldingi" va "Keyingi" tugmalarini foydalanuvchi tugmalaridan alohida qatorga joylashtiramiz
    navigation_buttons = []

    if int(start_index) >= 10:  # 10 dan katta bo'lsa
        previous_index = max(0, int(start_index) - 10)
        if previous_index < len(users):  # Indeks nolga teng yoki undan katta bo'lishi kerak
            navigation_buttons.append(
                InlineKeyboardButton(
                    text="Oldingi",
                    callback_data=f"prev_{previous_index}_{users[previous_index]['nomi']}_{users[previous_index]['qsimi']}"
                )
            )
    if end_index < len(users):
        navigation_buttons.append(
            InlineKeyboardButton(
                text="Keyingi",
                callback_data=f"next_{end_index}_{users[end_index]['nomi']}_{users[end_index]['qsimi']}"  # Keyingi 4ta foydalanuvchiga o'tish
            )
        )

    if navigation_buttons:
        builder.row(*navigation_buttons)

    return builder.as_markup()


adminpaneltug = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Kanal📋", callback_data="Kanali"),
            InlineKeyboardButton(text="admin👌", callback_data="adminli")
        ],
        [
            InlineKeyboardButton(text="statistika📊", callback_data="statistik"),
            InlineKeyboardButton(text="Anime🎥", callback_data="Animeyuklashga")
        ],
        [
            InlineKeyboardButton(text="Elon🖊", callback_data="elon_add"),
            InlineKeyboardButton(text="carta🆔", callback_data="carta")
        ],
        [
            InlineKeyboardButton(text="Shorts♦", callback_data="short_add"),
            InlineKeyboardButton(text="Post📍", callback_data="Post")
        ],
        [
            InlineKeyboardButton(text="nastroyka🔑", callback_data="nastroy")
        ]
    ]
)

kanalyesno = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Kanal Qoshish➕", callback_data="qoshdim")
        ],
        [
            InlineKeyboardButton(text='Kanal O`chirish➖', callback_data="ochirdim")
        ],
        [
            InlineKeyboardButton(text="Ortga◀", callback_data="orqadda")
        ]
    ]
)

orqada = InlineKeyboardMarkup(
    inline_keyboard=[
        [
           InlineKeyboardButton(text="Ortga◀", callback_data="oldinor")
        ]
    ]
)

kanaltugmasi = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="kanalumrga✅", callback_data="umrkanal"),
            InlineKeyboardButton(text="kanalvaqt✅", callback_data="Vaqtkanal")
        ],
        [
            InlineKeyboardButton(text="kanalobunachi✅", callback_data="kanalobuna"),
            InlineKeyboardButton(text="kanalmaxfiy✅", callback_data="kanalmax")
        ],
        [
            InlineKeyboardButton(text="boshqa tarmoqlar📦", callback_data="tarmoqde")
        ],
        [
            InlineKeyboardButton(text="Ortga◀", callback_data="orqada")
        ]
    ]
)


ijdimoiytarmoqlar = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Instagram", callback_data="instagram"),
            InlineKeyboardButton(text="facebook", callback_data="facebook")
        ],
        [
            InlineKeyboardButton(text="Youtube", callback_data="youtube"),
            InlineKeyboardButton(text="discord", callback_data="discord")
        ],
        [
            InlineKeyboardButton(text="Ortga◀", callback_data="orqadbuend")
        ]
    ]
)

uzb_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🔍anime izlash")
        ],
        [
            KeyboardButton(text="Free⚠", style='success'),
            KeyboardButton(text="Anime buyurma🎭", style='success')
        ],
        [
            KeyboardButton(text="⚙ Nastroyka", style="primary")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder='Marhamat ✅'
)

def nastroyka_menu(page=1):

    if page == 1:
        kb = [
            [InlineKeyboardButton(text="💳 Pul kiritish", callback_data="pul", icon_custom_emoji_id='128274', style='danger'), InlineKeyboardButton(text="👤 Hisobim", callback_data="hisob")],
            [InlineKeyboardButton(text="🛠 Admin", callback_data="adminjab")],
            [InlineKeyboardButton(text="▶", callback_data="menu_2")]
        ]

    elif page == 2:
        kb = [
            [InlineKeyboardButton(text="📺 Obuna", callback_data="obunalar"), InlineKeyboardButton(text="💾 Saqlanganlar", callback_data="saqlangan")],
            [InlineKeyboardButton(text="🎬 Shorts", callback_data="shorts")],
            [
                InlineKeyboardButton(text="◀", callback_data="menu_1"),
                InlineKeyboardButton(text="▶", callback_data="menu_3")
            ]
        ]

    elif page == 3:
        kb = [
            [InlineKeyboardButton(text="📢 Elon", callback_data="elon"), InlineKeyboardButton(text="💰 Reklama", callback_data="reklama")],
            [InlineKeyboardButton(text="👥 Referal", callback_data="referal")],
            [
                InlineKeyboardButton(text="◀", callback_data="menu_2"),
                InlineKeyboardButton(text="▶", callback_data="menu_4")
            ]
        ]

    elif page == 4:
        kb = [
            [InlineKeyboardButton(text="📊 Statistika", callback_data="stat"), InlineKeyboardButton(text="📅 Mening kundaligim", callback_data="kundalik")],
            [InlineKeyboardButton(text="🎲promokod", callback_data="promokobonus")],
            [InlineKeyboardButton(text="◀", callback_data="menu_3")]
        ]

    return InlineKeyboardMarkup(inline_keyboard=kb)

tillar = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿Uzbek", callback_data="uz"),
            InlineKeyboardButton(text="🇺🇸Engilish", callback_data="eng")
        ],
        [
            InlineKeyboardButton(text="🇷🇺Russia", callback_data="ru"),
            InlineKeyboardButton(text="🇸🇦Arab", callback_data="ar")
        ]
    ]
)

vaqt_tugma = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="⏱ Minut", callback_data="minut"),
            InlineKeyboardButton(text="📅 Kun", callback_data="kun")
        ],
        [
            InlineKeyboardButton(text="🗓 Hafta", callback_data="hafta"),
            InlineKeyboardButton(text="📆 Oy", callback_data="oy")
        ]
    ]
)

izlashuchun = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Nomi bn izlash🔍", callback_data="izlash", style="danger" ),
        ],
        [
            InlineKeyboardButton(text="janr boyicha🎭", callback_data="janr"),
            InlineKeyboardButton(text="codi boyicha🗓", callback_data="code")
        ],
        [
            InlineKeyboardButton(text="random anime🧨", callback_data="random")
        ],
        [
            InlineKeyboardButton(text="Kop korilganlar👁‍", callback_data='kop'),
            InlineKeyboardButton(text="Top animelar📊", callback_data="Top")
        ],
        [
            InlineKeyboardButton(text="Yil boyicha⏲", callback_data="Yil"),
            InlineKeyboardButton(text="Anonim qidiruv🔎", switch_inline_query_current_chat='')
        ]
    ]
)