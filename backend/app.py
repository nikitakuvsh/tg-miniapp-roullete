import asyncio
import logging

from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from aiogram.exceptions import TelegramAPIError

TELEGRAM_BOT_TOKEN = "8039605779:AAEm7vfc1eNRw5z9mDoPLSXa3no7W_r0Zh8"
WEB_APP_URL = "https://tg-miniapp-roullete.netlify.app/"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "FastAPI работает!"}

@dp.message(Command(commands=["start"]))
async def cmd_start(message: Message):
    web_app_button = KeyboardButton(
        text="Открыть мини-приложение 🎲",
        web_app=WebAppInfo(url=WEB_APP_URL)
    )
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[web_app_button]],
        resize_keyboard=True
    )

    try:
        await message.answer(
            "Привет! Откройте мини-приложение и приступайте к акции!",
            reply_markup=keyboard
        )
        await message.answer("⚠️ Это тестовая версия бота. Пользователи пока не сохраняются.")
    except TelegramAPIError as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")

async def start_bot():
    """Запуск Telegram бота (polling)"""
    await dp.start_polling(bot)

async def main():
    """Запуск FastAPI + Telegram бота"""
    import uvicorn

    config = uvicorn.Config(app=app, host="0.0.0.0", port=8000, log_level="info", reload=False)
    server = uvicorn.Server(config)

    # Запускаем FastAPI сервер и Telegram бота параллельно
    api_task = asyncio.create_task(server.serve())
    bot_task = asyncio.create_task(start_bot())

    await asyncio.gather(api_task, bot_task)

if __name__ == "__main__":
    asyncio.run(main())
