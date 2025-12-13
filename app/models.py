from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    passwords = relationship("PasswordEntry", back_populates="owner")

class PasswordEntry(Base):
    __tablename__ = "passwords"

    id = Column(Integer, primary_key=True, index=True)
    service = Column(String, index=True)
    username = Column(String)
    encrypted_password = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="passwords")