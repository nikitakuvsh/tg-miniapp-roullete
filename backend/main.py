from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from db import get_connection

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

@app.post("/claim")
def claim_prize(data: ClaimRequest):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM items WHERE id = %s", (data.item_id,))
    if cur.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Item not found")

    cur.execute("""
        INSERT INTO claims (email, item_id)
        VALUES (%s, %s)
    """, (data.email, data.item_id))

    conn.commit()
    conn.close()
    return {"message": "Промокод будет выслан на почту"}

@app.get("/ping")
def ping():
    return {"status": "ok", "message": "Server is alive"}
