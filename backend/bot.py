import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from aiogram.exceptions import TelegramAPIError
import httpx

TELEGRAM_BOT_TOKEN = "8039605779:AAEm7vfc1eNRw5z9mDoPLSXa3no7W_r0Zh8"
WEB_APP_URL = "https://tg-miniapp-roullete.netlify.app/"
BACKEND_API = "http://localhost:8000"  # поменяй, если надо

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
    chat_id = message.chat.id

    # Пришло ли сообщение с email для claim? Пример: /claim email@example.com
    if message.text and message.text.startswith("/claim"):
        parts = message.text.split()
        if len(parts) != 2:
            await message.reply("Используй команду так: /claim твоя_почта@example.com")
            return
        email = parts[1]

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(f"{BACKEND_API}/claim", json={"chat_id": chat_id, "email": email})
                resp.raise_for_status()
                data = resp.json()
                await message.answer(f"Промокод для {data['item_name']} отправлен на почту!")
            except httpx.HTTPStatusError as e:
                await message.answer(f"Ошибка: {e.response.json().get('detail', e.response.text)}")
            except Exception as e:
                await message.answer(f"Ошибка при отправке запроса: {e}")
        return

    # Если это обычное сообщение — попробуем сделать spin
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{BACKEND_API}/spin", json={"chat_id": chat_id})
            resp.raise_for_status()
            data = resp.json()
            if data["already_spun"]:
                await message.answer(f"Вы уже крутили рулетку и выиграли предмет с ID {data['item_id']}.\n" +
                                     "Для получения промокода введите команду:\n/claim твоя_почта@example.com")
            else:
                await message.answer(f"Вы крутите рулетку... Ваш приз - предмет с ID {data['item_id']}.\n" +
                                     "Чтобы получить промокод, введите команду:\n/claim твоя_почта@example.com")
        except Exception as e:
            await message.answer(f"Ошибка при обращении к backend: {e}")

async def start_bot():
    await dp.start_polling(bot)
