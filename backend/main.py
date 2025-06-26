# backend.py
import asyncpg
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import secrets
import string
import random
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "postgresql://tg_miniapp_roullete_bd_user:nyilaFOrUBtbQf3ybR3jRczDNwhB04PZ@dpg-d1e7rveuk2gs73adr1p0-a.oregon-postgres.render.com:5432/tg_miniapp_roullete_bd"

async def get_pool():
    if not hasattr(app.state, "db_pool"):
        app.state.db_pool = await asyncpg.create_pool(DATABASE_URL)
    return app.state.db_pool

class SpinRequest(BaseModel):
    chat_id: int

class ClaimRequest(BaseModel):
    chat_id: int
    email: EmailStr

def generate_promo_code(length=8):
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

async def send_promo_code_email(email: str, code: str, item_name: str):
    # Заглушка - в проде вставь свой mail sender
    print(f"Отправка промокода {code} за {item_name} на {email}")

@app.get("/items")
async def get_items():
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, name, probability, price, photo_url FROM items")
        return [dict(row) for row in rows]

@app.post("/spin")
async def spin(data: SpinRequest):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT item_id FROM user_prizes WHERE chat_id=$1", data.chat_id)
        if row:
            return {"already_spun": True, "item_id": row["item_id"]}

        items = await conn.fetch("SELECT id, probability FROM items")
        if not items:
            raise HTTPException(404, "Items not found")

        rand = random.random()
        acc = 0.0
        chosen_id = items[-1]["id"]
        for item in items:
            acc += item["probability"]
            if rand <= acc:
                chosen_id = item["id"]
                break

        await conn.execute(
            "INSERT INTO user_prizes(chat_id, item_id, claimed) VALUES ($1, $2, FALSE)",
            data.chat_id, chosen_id
        )
        return {"already_spun": False, "item_id": chosen_id}

@app.post("/claim")
async def claim(data: ClaimRequest):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT item_id, claimed FROM user_prizes WHERE chat_id=$1", data.chat_id)
        if not row:
            raise HTTPException(400, "You have not spun the wheel yet")
        if row["claimed"]:
            raise HTTPException(409, "Prize already claimed")

        item_id = row["item_id"]
        item_row = await conn.fetchrow("SELECT name FROM items WHERE id=$1", item_id)
        if not item_row:
            raise HTTPException(404, "Item not found")

        promo_code = generate_promo_code()
        try:
            await send_promo_code_email(data.email, promo_code, item_row["name"])
        except Exception as e:
            raise HTTPException(500, f"Email sending failed: {e}")

        await conn.execute(
            "UPDATE user_prizes SET email=$1, promo_code=$2, claimed=TRUE WHERE chat_id=$3",
            data.email, promo_code, data.chat_id
        )
        return {"message": "Promo code sent to email", "item_name": item_row["name"], "promo_code": promo_code}
