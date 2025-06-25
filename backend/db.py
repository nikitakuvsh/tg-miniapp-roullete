import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="roulette_db",
        user="postgres",
        password="2gecf232gecf2",
        cursor_factory=RealDictCursor
    )
