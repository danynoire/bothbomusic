# database.py
import os
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Boolean
)
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# 🔴 Proteção básica
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não definida no .env")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()


# =========================
# MODELO
# =========================
class GuildConfig(Base):
    __tablename__ = "guild_configs"

    guild_id = Column(Integer, primary_key=True, index=True)
    volume = Column(Integer, default=100)
    loop = Column(Boolean, default=False)


# =========================
# INIT
# =========================
def init_db():
    Base.metadata.create_all(bind=engine)


# =========================
# CRUD
# =========================
def get_guild_config(guild_id: int) -> GuildConfig:
    db = SessionLocal()
    try:
        config = db.query(GuildConfig).filter_by(guild_id=guild_id).first()
        if not config:
            config = GuildConfig(guild_id=guild_id)
            db.add(config)
            db.commit()
            db.refresh(config)
        return config
    finally:
        db.close()


def save_guild_config(
    guild_id: int,
    volume: int | None = None,
    loop: bool | None = None
):
    db = SessionLocal()
    try:
        config = db.query(GuildConfig).filter_by(guild_id=guild_id).first()
        if not config:
            config = GuildConfig(guild_id=guild_id)
            db.add(config)

        if volume is not None:
            config.volume = volume
        if loop is not None:
            config.loop = loop

        db.commit()
    finally:
        db.close()


# =========================
# 👉 ISSO QUE FALTAVA
# =========================
def get_all_guilds():
    db = SessionLocal()
    try:
        return db.query(GuildConfig).all()
    finally:
        db.close()
