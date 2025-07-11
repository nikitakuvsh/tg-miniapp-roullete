import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    return psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        database="roullete"
        user="postgres", 
        password="2gecf232gecf2",
        cursor_factory=RealDictCursor
    )
