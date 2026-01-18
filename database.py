# database.py
import os
from sqlalchemy import Column, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class GuildConfig(Base):
    __tablename__ = "guild_configs"

    guild_id = Column(Integer, primary_key=True, index=True)
    volume = Column(Integer, default=100)
    loop = Column(Boolean, default=False)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_guild_config(guild_id: int):
    db = SessionLocal()
    cfg = db.query(GuildConfig).filter_by(guild_id=guild_id).first()
    if not cfg:
        cfg = GuildConfig(guild_id=guild_id)
        db.add(cfg)
        db.commit()
        db.refresh(cfg)
    db.close()
    return cfg


def save_guild_config(guild_id: int, volume: int = None, loop: bool = None):
    db = SessionLocal()
    cfg = db.query(GuildConfig).filter_by(guild_id=guild_id).first()
    if not cfg:
        cfg = GuildConfig(guild_id=guild_id)
        db.add(cfg)

    if volume is not None:
        cfg.volume = volume
    if loop is not None:
        cfg.loop = loop

    db.commit()
    db.close()
