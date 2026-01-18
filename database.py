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

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS guild_configs (
        guild_id INTEGER PRIMARY KEY,
        volume INTEGER DEFAULT 50,
        loop_queue BOOLEAN DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

# 🔹 SALVAR CONFIG DO SERVIDOR
def save_guild_config(guild_id: int, volume: int = None, loop_queue: bool = None):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO guild_configs (guild_id) VALUES (?)",
        (guild_id,)
    )

    if volume is not None:
        cur.execute(
            "UPDATE guild_configs SET volume=? WHERE guild_id=?",
            (volume, guild_id)
        )

    if loop_queue is not None:
        cur.execute(
            "UPDATE guild_configs SET loop_queue=? WHERE guild_id=?",
            (int(loop_queue), guild_id)
        )

    conn.commit()
    conn.close()

# 🔹 CARREGAR CONFIG
def get_guild_config(guild_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT volume, loop_queue FROM guild_configs WHERE guild_id=?",
        (guild_id,)
    )

    row = cur.fetchone()
    conn.close()

    if row:
        return {
            "volume": row[0],
            "loop_queue": bool(row[1])
        }

    return {
        "volume": 50,
        "loop_queue": False
    }
