# renderfix
import sys
if sys.version_info >= (3, 13):
    import typing
    # Фикс для SQLAlchemy в Python 3.13
    if not hasattr(typing, 'TypingOnly'):
        class TypingOnly: pass
        typing.TypingOnly = TypingOnly
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv()
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY").encode()
fernet = Fernet(ENCRYPTION_KEY)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    passwords = relationship("PasswordEntry", back_populates="owner")


class PasswordEntry(Base):
    __tablename__ = "passwords"
    id = Column(Integer, primary_key=True, index=True)
    service = Column(String, index=True)
    username = Column(String)
    encrypted_password = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="passwords")

    def decrypt_password(self) -> str:
        return fernet.decrypt(self.encrypted_password.encode()).decode()