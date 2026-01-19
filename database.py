import sqlite3

conn = sqlite3.connect("data.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS guilds (
    guild_id INTEGER PRIMARY KEY,
    volume INTEGER DEFAULT 100,
    loop TEXT DEFAULT 'off'
)
""")
conn.commit()

def save_guild(gid, volume=100, loop="off"):
    cur.execute(
        "INSERT OR REPLACE INTO guilds VALUES (?, ?, ?)",
        (gid, volume, loop)
    )
    conn.commit()
