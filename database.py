from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from config import DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)

class GuildConfig(Base):
    __tablename__ = "guilds"
    id = Column(Integer, primary_key=True)
    prefix = Column(String, default="hb!")

Base.metadata.create_all(engine)
