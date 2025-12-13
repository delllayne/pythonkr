from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class PasswordCreate(BaseModel):
    service: str
    username: str
    password: str  # plaintext (будет зашифрован)

class PasswordUpdate(BaseModel):
    service: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

class PasswordOut(BaseModel):
    id: int
    service: str
    username: str

    class Config:
        from_attributes = True