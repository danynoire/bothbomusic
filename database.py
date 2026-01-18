import os
from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    future=True,
    echo=False
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    guild_id = Column(BigInteger, nullable=False)
    action = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def log_action(user_id: int, guild_id: int, action: str):
    db = SessionLocal()
    log = AuditLog(
        user_id=user_id,
        guild_id=guild_id,
        action=action
    )
    db.add(log)
    db.commit()
    db.close()

def get_logs(limit=100):
    db = SessionLocal()
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )
    db.close()
    return logs
