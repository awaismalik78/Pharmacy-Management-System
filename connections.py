import psycopg2
from config import config

def create_connection():
    """
    Establishes and returns a connection to the PostgreSQL database.
    Uses settings from the database.ini file.
    """
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        print("✅ Connected to the database successfully!")
    except psycopg2.Error as e:
        print("❌ Database connection failed:")
        print(e)
    return conn
