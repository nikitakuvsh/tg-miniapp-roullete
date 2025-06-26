from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import (
    Message,
    WebAppInfo,
    MenuButtonWebApp,
)
from aiogram.exceptions import TelegramAPIError
import logging
import asyncio

TELEGRAM_BOT_TOKEN = "8039605779:AAEm7vfc1eNRw5z9mDoPLSXa3no7W_r0Zh8"
WEB_APP_URL = "https://tg-miniapp-roullete.netlify.app/"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command(commands=["start"]))
async def cmd_start(message: Message):
    try:
        await message.answer("Привет! Открой мини-приложение через 📎 в меню.")
    except TelegramAPIError as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")

@dp.message()
async def handle_message(message: Message):
    chat_id = message.chat.id
    await message.answer(f"Ваш chat_id: {chat_id}")

async def on_startup():
    try:
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="🎰 Открыть рулетку",
                web_app=WebAppInfo(url=WEB_APP_URL)
            )
        )
        logging.info("Меню WebApp успешно установлено.")
    except TelegramAPIError as e:
        logging.error(f"Ошибка при установке меню WebApp: {e}")

async def start_bot():
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_bot())
