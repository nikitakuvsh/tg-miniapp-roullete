from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from aiogram.exceptions import TelegramAPIError
import logging

TELEGRAM_BOT_TOKEN = "8039605779:AAEm7vfc1eNRw5z9mDoPLSXa3no7W_r0Zh8"
WEB_APP_URL = "https://tg-miniapp-roullete.netlify.app/"

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
            "Привет! Откройте мини-приложение!",
            reply_markup=keyboard
        )
    except TelegramAPIError as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")

@dp.message()
async def handle_message(message: Message):
    chat_id = message.chat.id
    await message.answer(f"Ваш chat_id: {chat_id}")

async def start_bot():
    await dp.start_polling(bot)
