import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    return psycopg2.connect(
        host="dpg-d1e7rveuk2gs73adr1p0-a.oregon-postgres.render.com",
        port=5432,
        database="tg_miniapp_roullete_bd",
        user="tg_miniapp_roullete_bd_user",
        password="nyilaFOrUBtbQf3ybR3jRczDNwhB04PZ",
        cursor_factory=RealDictCursor
    )
