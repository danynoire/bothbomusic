import os
import sqlite3
from urllib.parse import urlparse

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    if DATABASE_URL:
        if DATABASE_URL.startswith("postgres"):
            import psycopg2
            return psycopg2.connect(DATABASE_URL)
        else:
            raise ValueError("DATABASE_URL não suportada")
    else:
        return sqlite3.connect("data.db")
