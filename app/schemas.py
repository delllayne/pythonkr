# renderfix
import sys
if sys.version_info >= (3, 13):
    import typing
    # Фикс для SQLAlchemy в Python 3.13
    if not hasattr(typing, 'TypingOnly'):
        class TypingOnly: pass
        typing.TypingOnly = TypingOnly
from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool
    class Config:
        from_attributes = True

class UserAdminCreate(BaseModel):
    username: str
    password: str

class PasswordCreate(BaseModel):
    service: str
    username: str
    password: str

class PasswordUpdate(BaseModel):
    service: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

class PasswordOut(BaseModel):
    id: int
    service: str
    username: str
    password: str
    class Config:
        from_attributes = True