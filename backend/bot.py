from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import (
    Message,
    WebAppInfo,
    MenuButtonWebApp,
    ChatMember,
)
from aiogram.exceptions import TelegramAPIError
import logging
import asyncio

TELEGRAM_BOT_TOKEN = "8039605779:AAEm7vfc1eNRw5z9mDoPLSXa3no7W_r0Zh8"
#WEB_APP_URL = "http://80.93.187.149:8080/"
WEB_APP_URL = "https://tg-miniapp-roullete.netlify.app"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# CHANNEL_USERNAME = "@laifenrussia"

# async def is_user_subscribed(user_id: int) -> bool:
#     try:
#         member: ChatMember = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
#         return member.status in ["member", "administrator", "creator"]
#     except TelegramAPIError as e:
#         logging.warning(f"Ошибка проверки подписки: {e}")
#         return False

@dp.message(Command(commands=["start"]))
async def cmd_start(message: Message):
    user_id = message.from_user.id

    # if not await is_user_subscribed(user_id):
    #     await message.answer("Чтобы играть в рулетку, подпишитесь на наш канал: https://t.me/laifenrussia и снова нажмите /start")
    #     return

    try:
        await message.answer("Привет! Открой мини-приложение через 📎 в меню.")
    except TelegramAPIError as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")

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
