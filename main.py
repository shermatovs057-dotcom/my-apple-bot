import asyncio
import random
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiohttp import web

# --- SOZLAMALAR ---
API_TOKEN = '8762808712:AAHf4E6THer_pl8aeXUl947RsUlXKbGmx7g'
ADMIN_ID = 5476312450
PROMO_CODE = "1x_4833871"
# O'zingizning Telegram lichkangizni yozing
MY_LICHKA = "https://t.me/ii_rood" 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

verified_users = set()

class RegistrationStates(StatesGroup):
    waiting_for_screenshot = State()

# --- UC NARXLARI VA REKLAMA ---
UC_PRICES_TEXT = (
    "💎 **PUBG MOBILE UC NARXLARI** 💎\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "📦 60 UC — 12,000 so'm\n"
    "📦 325 UC — 55,000 so'm\n"
    "📦 660 UC — 105,000 so'm\n"
    "📦 1800 UC — 270,000 so'm\n"
    "📦 3850 UC — 530,000 so'm\n"
    "📦 8100 UC — 1,050,000 so'm\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "🚀 *To'lovdan so'ng 5-10 daqiqada tushadi!*\n"
    "⚠️ Narxlar kursga qarab o'zgarishi mumkin."
)

AD_TEXT = f"\n\n💎 **ARZON UC KERAKMI?**\n👉 [NARXLARNI KO'RISH](t.me/share/url?url={MY_LICHKA})"

# --- ALGORITM ---
def generate_apple_grid():
    grid = "```\n"
    for i in range(10, 0, -1):
        win_pos = random.randint(0, 4)
        cells = ["🍎" if pos == win_pos else "▫️" for pos in range(5)]
        grid += f"{i:02d} | {' '.join(cells)} |\n"
    grid += "```"
    return grid + AD_TEXT

# --- KLAVIATURALAR ---
def get_refresh_keyboard(platform):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔄 QAYTA TAHLIL", callback_data=f"verify:{platform}"))
    builder.row(types.InlineKeyboardButton(text="💎 UC SOTIB OLISH", url=MY_LICHKA))
    builder.row(types.InlineKeyboardButton(text="🏠 ASOSIY MENYU", callback_data="start_apple"))
    return builder.as_markup()

def get_uc_buy_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🛒 SOTIB OLISH (LICHKA)", url=MY_LICHKA))
    builder.row(types.InlineKeyboardButton(text="⬅️ ORQAGA", callback_data="back_to_start"))
    return builder.as_markup()

# --- HANDLERLAR ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await show_main_menu(message)

@dp.callback_query(F.data == "back_to_start")
async def back_to_start(callback: types.CallbackQuery):
    await callback.message.edit_text(f"👋 Salom {callback.from_user.first_name}!\nAnaliz olish uchun tugmani bosing:", 
                                     reply_markup=main_menu_kb())

def main_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🍎 APPLE OF FORTUNE", callback_data="start_apple"))
    builder.row(types.InlineKeyboardButton(text="💎 UC NARXLARI", callback_data="show_uc_prices"))
    return builder.as_markup()

async def show_main_menu(message: types.Message):
    await message.answer(f"👋 Salom {message.from_user.first_name}!\nKerakli bo'limni tanlang:", reply_markup=main_menu_kb())

@dp.callback_query(F.data == "show_uc_prices")
async def show_prices(callback: types.CallbackQuery):
    await callback.message.edit_text(UC_PRICES_TEXT, reply_markup=get_uc_buy_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data == "start_apple")
async def choose_platform(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    # MOSTBET o'rniga 888STARZ qo'shildi
    platforms = ["1XBET", "LINEBET", "MELBET", "888STARZ"]
    for p in platforms:
        builder.row(types.InlineKeyboardButton(text=p, callback_data=f"verify:{p}"))
    builder.row(types.InlineKeyboardButton(text="⬅️ ORQAGA", callback_data="back_to_start"))
    await callback.message.edit_text("❓ Platformani tanlang:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("verify:"))
async def check_user(callback: types.CallbackQuery, state: FSMContext):
    platform = callback.data.split(":")[1]
    
    if callback.from_user.id in verified_users:
        grid = generate_apple_grid()
        await callback.message.edit_text(
            f"✅ **{platform} TAHLILI:**\n{grid}\n\nEslatib o'tamiz yutuqni xohlagan vaqtingizda olishingiz mumkin!", 
            parse_mode="Markdown",
            reply_markup=get_refresh_keyboard(platform)
        )
    else:
        msg = (f"📩 **Tekshiruv!**\n\n**{platform}** ID raqamingiz ko'ringan rasm yuboring.\n"
               f"⚠️ **PROMO-KOD:** `{PROMO_CODE}`\n\n"
               f"💎 **Arzon UC servis:** [NARXLARNI KO'RISH]({MY_LICHKA})")
        await callback.message.edit_text(msg, parse_mode="Markdown")
        await state.update_data(plat=platform)
        await state.set_state(RegistrationStates.waiting_for_screenshot)

@dp.message(RegistrationStates.waiting_for_screenshot, F.photo)
async def handle_screenshot(message: types.Message, state: FSMContext):
    data = await state.get_data()
    platform = data.get('plat', '1XBET')
    verified_users.add(message.from_user.id)
    
    try:
        await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"🔔 Yangi rasm: {message.from_user.full_name}\nPlat: {platform}")
    except: pass

    grid = generate_apple_grid()
    await message.answer(f"✅ Tasdiqlandi!\n\n🍎 **{platform} ANALIZ:**\n{grid}", 
                         parse_mode="Markdown", 
                         reply_markup=get_refresh_keyboard(platform))
    await state.clear()

# --- WEB SERVER (Render uchun) ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 8080)))
    await site.start()

# --- ASOSIY ISHGA TUSHIRISH ---
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(start_web_server()) 
    print("--- BOT ISHLADI ---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
