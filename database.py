import logging
from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Boolean, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime

from config import Config

log = logging.getLogger("KanhaManager.DB")

engine = create_engine(Config.DATABASE_URL, pool_pre_ping=True)
Base = declarative_base()
Session = scoped_session(sessionmaker(bind=engine))

# ─── MODELS ───────────────────────────────────────────────

class WelcomeSetting(Base):
    __tablename__ = "welcome_settings"
    chat_id = Column(BigInteger, primary_key=True)
    welcome_enabled = Column(Boolean, default=True)
    welcome_message = Column(Text, default="Welcome {mention} to {chat}!")
    goodbye_enabled = Column(Boolean, default=False)
    goodbye_message = Column(Text, default="Goodbye {first}!")

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger)
    name = Column(String(64))
    content = Column(Text)

class Filter(Base):
    __tablename__ = "filters"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger)
    keyword = Column(String(128))
    reply = Column(Text)

class WarnSetting(Base):
    __tablename__ = "warn_settings"
    chat_id = Column(BigInteger, primary_key=True)
    warn_limit = Column(Integer, default=3)
    warn_mode = Column(String(16), default="ban")  # ban / kick / mute

class UserWarn(Base):
    __tablename__ = "user_warns"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger)
    user_id = Column(BigInteger)
    reason = Column(Text, default="")
    warned_at = Column(DateTime, default=datetime.utcnow)

class BlacklistWord(Base):
    __tablename__ = "blacklist_words"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger)
    word = Column(String(128))

class LockSetting(Base):
    __tablename__ = "lock_settings"
    chat_id = Column(BigInteger, primary_key=True)
    sticker = Column(Boolean, default=False)
    gif = Column(Boolean, default=False)
    photo = Column(Boolean, default=False)
    video = Column(Boolean, default=False)
    audio = Column(Boolean, default=False)
    document = Column(Boolean, default=False)
    voice = Column(Boolean, default=False)
    url = Column(Boolean, default=False)
    forward = Column(Boolean, default=False)
    bot = Column(Boolean, default=False)

class FloodSetting(Base):
    __tablename__ = "flood_settings"
    chat_id = Column(BigInteger, primary_key=True)
    limit = Column(Integer, default=0)  # 0 = disabled
    mode = Column(String(16), default="mute")

class FloodCount(Base):
    __tablename__ = "flood_counts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger)
    user_id = Column(BigInteger)
    count = Column(Integer, default=0)
    last_msg_id = Column(Integer, default=0)

# ─── CREATE ALL TABLES ────────────────────────────────────
Base.metadata.create_all(engine)
log.info("Database tables created/verified.")

# ─── DB HELPERS ───────────────────────────────────────────

def get_session():
    return Session()

def close_session():
    Session.remove()
