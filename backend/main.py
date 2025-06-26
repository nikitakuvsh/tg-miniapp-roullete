from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from db import get_connection
import secrets
import string
from email_utils import send_promo_code_email
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ClaimRequest(BaseModel):
    email: EmailStr
    item_id: int

@app.get("/items")
def get_items():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, probability, price, photo_url FROM items")
    items = cur.fetchall()
    conn.close()

    return items

def generate_promo_code(length=8):
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

@app.post("/claim")
async def claim_prize(data: ClaimRequest):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT name FROM items WHERE id = %s", (data.item_id,))
    item_row = cur.fetchone()
    if not item_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Item not found")

    item_name = item_row[0]

    # Проверяем, есть ли уже запись
    cur.execute("SELECT id FROM claims WHERE email = %s AND item_id = %s", (data.email, data.item_id))
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=409, detail="You have already claimed this item.")

    promo_code = generate_promo_code()

    try:
        # Отправляем почту до сохранения
        await send_promo_code_email(data.email, promo_code, item_name)
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Ошибка отправки почты: {e}")

    cur.execute(
        "INSERT INTO claims (email, item_id, promo_code) VALUES (%s, %s, %s)",
        (data.email, data.item_id, promo_code)
    )
    conn.commit()
    conn.close()

    return {"message": "Промокод отправлен на почту", "item_name": item_name}



@app.get("/ping")
def ping():
    return {"status": "ok", "message": "Server is alive"}
