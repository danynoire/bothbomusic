import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class GuildConfig(Base):
    __tablename__ = "guild_configs"

    guild_id = Column(Integer, primary_key=True)
    prefix = Column(String, default="hb!")
    loop = Column(Boolean, default=False)
    volume = Column(Integer, default=100)

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

def set_loop(guild_id: int, value: bool):
    db = SessionLocal()
    cfg = db.query(GuildConfig).filter_by(guild_id=guild_id).first()
    if cfg:
        cfg.loop = value
        db.commit()
    db.close()

def get_all_guilds():
    db = SessionLocal()
    guilds = db.query(GuildConfig).all()
    db.close()
    return guilds
