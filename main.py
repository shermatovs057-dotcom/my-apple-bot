import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# --- SOZLAMALAR ---
API_TOKEN = '8762808712:AAHf4E6THer_pl8aeXUl947RsUlXKbGmx7g' 
ADMIN_ID = 5476312450 
PROMO_CODE = "APPLE77"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

verified_users = set()

class RegistrationStates(StatesGroup):
    waiting_for_screenshot = State()

# --- ALGORITM ---
def generate_apple_grid():
    grid = "```\n"
    for i in range(10, 0, -1):
        win_pos = random.randint(0, 4)
        cells = ["🍎" if pos == win_pos else "▫️" for pos in range(5)]
        grid += f"{i:02d} | {' '.join(cells)} |\n"
    grid += "```"
    return grid

# --- QAYTA ANALIZ TUGMASI ---
def get_refresh_keyboard(platform):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔄 QAYTA TAHLIL", callback_data=f"verify:{platform}"))
    builder.row(types.InlineKeyboardButton(text="🏠 ASOSIY MENYU", callback_data="start_apple"))
    return builder.as_markup()

# --- HANDLERLAR ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🍎 APPLE OF FORTUNE", callback_data="start_apple"))
    await message.answer(f"👋 Salom {message.from_user.first_name}!\nAnaliz olish uchun tugmani bosing:", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "start_apple")
async def choose_platform(callback: types.CallbackQuery):
    await callback.answer()
    builder = InlineKeyboardBuilder()
    for p in ["1XBET", "LINEBET", "MELBET", "MOSTBET"]:
        builder.row(types.InlineKeyboardButton(text=p, callback_data=f"verify:{p}"))
    await callback.message.edit_text("❓ Platformani tanlang:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("verify:"))
async def check_user(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    platform = callback.data.split(":")[1]
    
    # Agar foydalanuvchi avval rasm yuborgan bo'lsa
    if callback.from_user.id in verified_users:
        grid = generate_apple_grid()
        # Xabarni tahrirlash (yangi analiz bilan)
        await callback.message.edit_text(
            f"✅ **{platform} TAHLILI:**\n{grid}\n\nYangi tahlil olish uchun pastdagi tugmani bosing:", 
            parse_mode="Markdown",
            reply_markup=get_refresh_keyboard(platform)
        )
        await callback.message.edit_text(
            f"✅ **{platform} TAHLILI:**\n{grid}\n\nEslatib o'tamiz yutuqni hohlagan vaqtingizda olshingiz mumkin!:", 
            parse_mode="Markdown",
            reply_markup=get_refresh_keyboard(platform)
        )
    else:
        # Rasm so'rash
        msg = (f"📩 **Tekshiruv!**\n\n**{platform}** ID raqamingiz ko'ringan rasm yuboring.\n"
               f"⚠️ **PROMO-KOD:** {PROMO_CODE}")
        await callback.message.edit_text(msg)
        await state.update_data(plat=platform)
        await state.set_state(RegistrationStates.waiting_for_screenshot)

@dp.message(RegistrationStates.waiting_for_screenshot, F.photo)
async def handle_screenshot(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    platform = data.get('plat', '1XBET')
    verified_users.add(user_id) # Foydalanuvchini tasdiqlash
    
    # Adminga yuborish
    try:
        await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"🔔 Yangi rasm: {message.from_user.full_name}\nPlat: {platform}")
    except: pass

    grid = generate_apple_grid()
    await message.answer(f"✅ Tasdiqlandi!\n\n🍎 **{platform} ANALIZ:**\n{grid}", 
                         parse_mode="Markdown", 
                         reply_markup=get_refresh_keyboard(platform))
    await state.clear()

async def main():
    await bot.delete_webhook(drop_pending_updates=True) # 2 marta kelishini oldini olish
    print("--- BOT ISHLADI ---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

# ulash telegram

import os
from aiohttp import web

async def handle(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 8080)))
    await site.start()

# main() funksiyasi ichida:
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(start_web_server()) # Web serverni ishga tushirish
    await dp.start_polling(bot)