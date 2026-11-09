import asyncio
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ==================== KLAVIATURALAR ====================

def main_menu() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="👤 Men haqimda"), KeyboardButton(text="💻 Xizmatlarim")],
        [KeyboardButton(text="🌐 Sayt buyurtma qilish"), KeyboardButton(text="🎓 Kurslarim")],
        [KeyboardButton(text="📝 Kursga yozilish"), KeyboardButton(text="🚀 Loyihalarim")],
        [KeyboardButton(text="📩 Bog'lanish")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def back_menu() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text="⬅️ Ortga"), KeyboardButton(text="🏠 Asosiy menyu")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# ==================== FSM HOLATLARI ====================

class OrderSite(StatesGroup):
    name = State()
    site_type = State()

class EnrollCourse(StatesGroup):
    name = State()
    course = State()

# ==================== YORDAMCHI FUNKSIYA ====================

def get_user_info(message: Message) -> dict:
    user = message.from_user
    username = user.username
    if username:
        profile = f"@{username} (https://t.me/{username})"
    else:
        profile = f"tg://user?id={user.id}"
    return {
        "telegram_id": user.id,
        "username": username or "yo'q",
        "profile": profile,
    }

# ==================== ASOSIY MENYU ====================

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        f"Assalomu alaykum, {message.from_user.first_name}! 👋\n\n"
        "Men Shanur Karimovning shaxsiy botiman.\n"
        "Quyidagi bo'limlardan birini tanlang:",
        reply_markup=main_menu(),
    )

@dp.message(F.text == "🏠 Asosiy menyu")
async def home_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🏠 Asosiy menyu", reply_markup=main_menu())

@dp.message(F.text == "⬅️ Ortga")
async def back_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🏠 Asosiy menyu", reply_markup=main_menu())

# ==================== 1. MEN HAQIMDA ====================

@dp.message(F.text == "👤 Men haqimda")
async def about_handler(message: Message):
    text = (
        "👤 <b>Shanur Karimov</b>\n\n"
        "💼 <b>Kasbiy yo'nalish:</b> Developer\n"
        "💡 <b>Daraja:</b> Midle\n"
        "🛠 <b>O'rganayotgan texnologiyalar:</b> Backend\n"
    )
    await message.answer(text, reply_markup=back_menu(), parse_mode="HTML")

# ==================== 2. XIZMATLARIM ====================

@dp.message(F.text == "💻 Xizmatlarim")
async def services_handler(message: Message):
    text = (
        "💻 <b>Xizmatlarim</b>\n\n"
        "1. <b>Landing page</b>\n"
        "2. <b>Portfolio sayt</b> \n"
        "3. <b>Biznes sayt</b> \n"
        "4. <b>Telegram bot</b>\n"
        "5. <b>Maxsus web loyihalar</b> \n"
    )
    await message.answer(text, reply_markup=back_menu(), parse_mode="HTML")

# ==================== 3. SAYT BUYURTMA QILISH (FSM) ====================

@dp.message(F.text == "🌐 Sayt buyurtma qilish")
async def order_start(message: Message, state: FSMContext):
    await state.set_state(OrderSite.name)
    await message.answer("Ismingizni kiriting:", reply_markup=back_menu())

@dp.message(OrderSite.name)
async def order_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(OrderSite.site_type)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Landing page", callback_data="site_landing")],
        [InlineKeyboardButton(text="Portfolio sayt", callback_data="site_portfolio")],
        [InlineKeyboardButton(text="Biznes sayt", callback_data="site_biznes")],
        [InlineKeyboardButton(text="Telegram bot", callback_data="site_bot")],
        [InlineKeyboardButton(text="Maxsus loyiha", callback_data="site_maxsus")],
    ])
    await message.answer("Sayt turini tanlang:", reply_markup=kb)

@dp.callback_query(OrderSite.site_type, F.data.startswith("site_"))
async def order_type(callback: CallbackQuery, state: FSMContext):
    site_map = {
        "site_landing": "Landing page",
        "site_portfolio": "Portfolio sayt",
        "site_biznes": "Biznes sayt",
        "site_bot": "Telegram bot",
        "site_maxsus": "Maxsus loyiha",
    }
    site_type = site_map.get(callback.data, callback.data)
    data = await state.get_data()
    user = get_user_info(callback.message)

    admin_text = (
        "🆕 <b>Yangi ariza — Sayt buyurtmasi</b>\n\n"
        f"👤 Ism: {data['name']}\n"
        f"📱 Telefon: {data['phone']}\n"
        f"📌 Sayt turi: {site_type}\n"
        "Adminga murojat qiling: @shanurkarimov\n"

        f"🕐 Vaqt: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    )
    await bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML")

    await callback.message.answer(
        "✅ Arizangiz muvaffaqiyatli yuborildi! Tez orada siz bilan bog'lanaman.",
        reply_markup=main_menu(),
    )
    await state.clear()
    await callback.answer()

# ==================== 4. KURSLARIM ====================

@dp.message(F.text == "🎓 Kurslarim")
async def courses_handler(message: Message):
    text = (
        "🎓 <b>Kurslarim</b>\n\n"
        "<b>Kurs nomi:</b> Frontent, Python\n"
        "<b>Tavsif:</b> Dasdurlashni noldan organing\n"
        "📝 Kursga yozilish uchun pastdagi tugmani bosing."
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Kursga yozilish", callback_data="enroll_start")]
    ])
    await message.answer(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data == "enroll_start")
async def enroll_from_courses(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EnrollCourse.name)
    await callback.message.answer("Ismingizni kiriting:", reply_markup=back_menu())
    await callback.answer()

# ==================== 5. KURSGA YOZILISH (FSM) ====================

@dp.message(F.text == "📝 Kursga yozilish")
async def enroll_start(message: Message, state: FSMContext):
    await state.set_state(EnrollCourse.name)
    await message.answer("Ismingizni kiriting:", reply_markup=back_menu())

@dp.message(EnrollCourse.name)
async def enroll_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(EnrollCourse.course)
    await message.answer("Qaysi kursga yozilmoqchisiz? Kurs nomini kiriting:")

@dp.message(EnrollCourse.course)
async def enroll_course(message: Message, state: FSMContext):
    data = await state.get_data()
    user = get_user_info(message)

    admin_text = (
        "🆕 <b>Yangi ariza — Kursga yozilish</b>\n\n"
        f"👤 Ism: {data['name']}\n"
        f"📱 Telefon: {data['phone']}\n"
        f"📌 Kurs: {message.text}\n"
        f"🆔 Telegram ID: {user['telegram_id']}\n"
        f"🔗 Profil: {user['profile']}\n"
        f"🕐 Vaqt: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    await bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML")

    await message.answer(
        "✅ Arizangiz muvaffaqiyatli yuborildi! Tez orada siz bilan bog'lanaman.",
        reply_markup=main_menu(),
    )
    await state.clear()

# ==================== 6. LOYIHALARIM ====================

@dp.message(F.text == "🚀 Loyihalarim")
async def projects_handler(message: Message):
    text = (
        "🚀 <b>Loyihalarim</b>\n\n"
        "<b>Dokon:</b> https://karimovjs.github.io/Karimov-store/\n"
        "<b>Portfoliyo:</b> https://karimovjs.github.io/My.Portfoliyo/\n"
    )
    await message.answer(text, reply_markup=back_menu(), parse_mode="HTML")

# ==================== 7. BOG'LANISH ====================

@dp.message(F.text == "📩 Bog'lanish")
async def contact_handler(message: Message):
    text = (
        "📩 <b>Bog'lanish</b>\n\n"
        "Telegram: @shanurkarimov\n"
        "Instagram: https://www.instagram.com/shanur_karimov\n"
        
    )
    await message.answer(text, reply_markup=back_menu(), parse_mode="HTML")

# ==================== ISHGA TUSHIRISH ====================

async def main():
    print("Bot ishga tushmoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())