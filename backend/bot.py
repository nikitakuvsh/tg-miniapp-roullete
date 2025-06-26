from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from aiogram.exceptions import TelegramAPIError
import httpx
import logging

TELEGRAM_BOT_TOKEN = "8039605779:AAEm7vfc1eNRw5z9mDoPLSXa3no7W_r0Zh8"
WEB_APP_URL = "https://tg-miniapp-roullete.netlify.app/"
BACKEND_API = "https://tg-miniapp-roullete.onrender.com"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command(commands=["start"]))
async def cmd_start(message: Message):
    web_app_button = KeyboardButton(
        text="Открыть мини-приложение 🎲",
        web_app=WebAppInfo(url=WEB_APP_URL)
    )
    keyboard = ReplyKeyboardMarkup(keyboard=[[web_app_button]], resize_keyboard=True)

    try:
        await message.answer(
            "Привет! Откройте мини-приложение и приступайте к акции!",
            reply_markup=keyboard
        )
        await message.answer("⚠️ Это тестовая версия бота. Пользователи пока не сохраняются.")
    except TelegramAPIError as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")

@dp.message()
async def handle_message(message: Message):
    chat_id = message.chat.id  # Вот тут ты просто берёшь chat_id из сообщения — всё просто и понятно

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{BACKEND_API}/spin", json={"chat_id": chat_id})
            resp.raise_for_status()
            data = resp.json()

            if data.get("already_spun"):
                await message.answer(f"Вы уже крутили рулетку и выиграли предмет с ID {data['item_id']}.")
            else:
                await message.answer(f"Вы крутите рулетку... Ваш приз - предмет с ID {data['item_id']}.")
        except Exception as e:
            await message.answer(f"Ошибка при обращении к backend: {e}")

async def start_bot():
    await dp.start_polling(bot)
