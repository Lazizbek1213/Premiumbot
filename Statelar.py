from aiogram.filters.state import State, StatesGroup

class umr(StatesGroup):
    umrk = State()
    umrb = State()
    umrt = State()

class adminjon1(StatesGroup):
    adminnomi = State()

class adminbek(StatesGroup):
    adminol = State()

class vaqtKa(StatesGroup):
    vaqtK = State()
    VaqtK1 = State()
    VaqtK2 = State()

class Kanal(StatesGroup):
    nomi = State()        # kanal nomi
    username = State()    # kanal username
    sub_count = State()

class privet(StatesGroup):

    user = State()      # kanal nomi
    add = State()  # kanal username (@kanal)
    aprivet = State()

class IjtimoiyState(StatesGroup):
    link = State()

class Yuklash(StatesGroup):
    photo = State()
    video_optional = State()
    soni = State()
    qsmi = State()
    janr = State()
    tili = State()
    yili = State()
    kod = State()
    video = State()
    Yuklash = State()

class UpdateAnime(StatesGroup):
    code = State()           # Yangilamoqchi bo‘lgan anime kodi
    qsmi_count = State()
    inln = State()# Qancha qism video qo‘shmoqchi
    upload_video = State()   # Video yuklash bosqichi
    post_choice = State()    # Post qilinsinmi? (rasm/video/yo'q)
    channel = State()
    upload_photo = State()
    # Kanal username yoki ID sorash

# ------------------ O‘CHIRISH FSM ------------------
class Ochirsh(StatesGroup):
    qod = State()           # O‘chirmoqchi bo‘lgan anime kodi
    qsmi = State()    # Qaysi qismni o‘chirmoqchi
    anime_code = State()

class Deposit(StatesGroup):
    amount = State()
    check = State()
    comment = State()

class CartaState(StatesGroup):
    add = State()

class nomi1(StatesGroup):
    nomi = State()


# Janr bilan izlash
class janrlar(StatesGroup):
    janr = State()


# Code bilan izlash
class code1(StatesGroup):
    code = State()


# Yil bilan izlash
class Yili(StatesGroup):
    yili = State()


# Qism yuborish uchun
class messageqsim(StatesGroup):
    message = State()


# Keyin eslatish uchun
class keyin(StatesGroup):
    keyin = State()


# Kundalik anime uchun
class kundalik(StatesGroup):
    kundalika = State()
    vaqt = State()

class AdminBalance(StatesGroup):
    user_id = State()
    amount = State()

class PromoStates(StatesGroup):
    waiting_code_name = State()
    waiting_amount = State()
    waiting_time_unit = State()
    waiting_time_value = State()

class Promokodish(StatesGroup):
    ishlatish = State()

class ElonState(StatesGroup):
    text = State()

class ShortState(StatesGroup):
    video = State()
    caption = State()
    code = State()

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

class Postniyoqotish(StatesGroup):
    ochirish = State()
