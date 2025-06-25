from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from db import get_connection

app = FastAPI()

# Разрешим CORS для фронта
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # в проде лучше указать конкретный домен
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

    # Если items — список словарей, то можно сразу вернуть
    return items



@app.post("/claim")
def claim_prize(data: ClaimRequest):
    conn = get_connection()
    cur = conn.cursor()

    # Проверим, существует ли товар
    cur.execute("SELECT id FROM items WHERE id = %s", (data.item_id,))
    if cur.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Item not found")

    # Сохраняем email и item_id в отдельную таблицу claims (опционально)
    cur.execute("""
        INSERT INTO claims (email, item_id)
        VALUES (%s, %s)
    """, (data.email, data.item_id))

    conn.commit()
    conn.close()
    return {"message": "Промокод будет выслан на почту"}
