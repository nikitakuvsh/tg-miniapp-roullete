import asyncpg
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import secrets
import string
import random
import hmac
import hashlib
from urllib.parse import parse_qsl
from email_utils import send_promo_code_email

app = FastAPI()

BOT_TOKEN = "8039605779:AAEm7vfc1eNRw5z9mDoPLSXa3no7W_r0Zh8"

# Разрешаем кросс-доменные запросы (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Строка подключения к PostgreSQL (твоя)
DATABASE_URL = "postgresql://tg_miniapp_roullete_bd_user:nyilaFOrUBtbQf3ybR3jRczDNwhB04PZ@dpg-d1e7rveuk2gs73adr1p0-a.oregon-postgres.render.com:5432/tg_miniapp_roullete_bd"

# Создаём пул соединений один раз при старте
@app.on_event("startup")
async def startup():
    app.state.db_pool = await asyncpg.create_pool(DATABASE_URL)

# Закрываем пул при завершении
@app.on_event("shutdown")
async def shutdown():
    await app.state.db_pool.close()

async def get_pool():
    return app.state.db_pool

# Запрос для кручения рулетки
class SpinRequest(BaseModel):
    chat_id: int

# Запрос для подтверждения приза и отправки email
class ClaimRequest(BaseModel):
    chat_id: int
    email: EmailStr

# Запрос для аутентификации по init_data от Telegram Mini App
class InitData(BaseModel):
    init_data: str

# Функция генерации промокода
def generate_promo_code(length=8):
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

# Получить все доступные предметы
@app.get("/items")
async def get_items():
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, name, probability, price, photo_url, quantity FROM items"
        )
        return [dict(row) for row in rows]
    
#Проверка крутил ли уже пользователь или нет    
@app.get("/has_spun")
async def has_spun(chat_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT item_id FROM spins WHERE chat_id = $1", chat_id)
        if row:
            return {"already_spun": True, "item_id": row["item_id"]}
        return {"already_spun": False}
    
# Крутим рулетку
@app.post("/spin")
async def spin(data: SpinRequest):
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Проверяем, крутил ли пользователь уже
        row = await conn.fetchrow("SELECT item_id FROM user_prizes WHERE chat_id=$1", data.chat_id)
        if row:
            return {"already_spun": True, "item_id": row["item_id"]}

        # Получаем только призы с quantity > 0
        items = await conn.fetch("SELECT id, probability FROM items WHERE quantity > 0")
        if not items:
            raise HTTPException(status_code=404, detail="Нет доступных призов")

        # Случайный выбор приза по вероятности
        rand = random.random()
        acc = 0.0
        chosen_id = items[-1]["id"]  # fallback — последний приз
        for item in items:
            acc += item["probability"]
            if rand <= acc:
                chosen_id = item["id"]
                break

        # Записываем результат для пользователя
        await conn.execute(
            "INSERT INTO user_prizes(chat_id, item_id, claimed) VALUES ($1, $2, FALSE)",
            data.chat_id, chosen_id
        )
        return {"already_spun": False, "item_id": chosen_id}

@app.post("/claim")
async def claim(data: ClaimRequest):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT item_id, claimed, promo_code, email FROM user_prizes WHERE chat_id=$1", data.chat_id
        )
        if not row:
            raise HTTPException(status_code=400, detail="Вы ещё не крутили рулетку")

        item_name = await conn.fetchval("SELECT name FROM items WHERE id=$1", row["item_id"])
        if not item_name:
            raise HTTPException(status_code=404, detail="Приз не найден")

        promo_code = row["promo_code"]

        # Если промокод ещё не создан — создаём новый и обновляем базу
        if not row["claimed"] or not promo_code:
            promo_code = generate_promo_code()
            await conn.execute(
                "UPDATE user_prizes SET email=$1, promo_code=$2, claimed=TRUE WHERE chat_id=$3",
                data.email, promo_code, data.chat_id
            )
        else:
            # Обновим email, если он отличается (чтобы отправлять на актуальный)
            if data.email != row["email"]:
                await conn.execute(
                    "UPDATE user_prizes SET email=$1 WHERE chat_id=$2",
                    data.email, data.chat_id
                )

        # Отправляем промокод по почте (в любом случае)
        try:
            await send_promo_code_email(data.email, promo_code, item_name)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Не удалось отправить email: {e}")

        return {"message": "Промокод отправлен", "item_name": item_name, "promo_code": promo_code}

@app.get("/ping")
def ping():
    return {"status": "ok", "message": "Server is alive"}