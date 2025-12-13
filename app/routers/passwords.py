from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal
from app.models import PasswordEntry
from app.schemas import PasswordCreate, PasswordOut, PasswordUpdate
from app.auth import get_current_user
from cryptography.fernet import Fernet
from app.database import get_db
import os
from dotenv import load_dotenv

load_dotenv()
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY").encode()
fernet = Fernet(ENCRYPTION_KEY)

router = APIRouter(prefix="/passwords", tags=["passwords"], dependencies=[Depends(get_current_user)])

def encrypt_password(password: str) -> str:
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(encrypted: str) -> str:
    return fernet.decrypt(encrypted.encode()).decode()

@router.post("/", response_model=PasswordOut, summary="Создать новую запись с паролем")
async def create_password(
    password_data: PasswordCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(SessionLocal)
):
    encrypted = encrypt_password(password_data.password)
    db_password = PasswordEntry(
        service=password_data.service,
        username=password_data.username,
        encrypted_password=encrypted,
        owner_id=current_user.id
    )
    db.add(db_password)
    await db.commit()
    await db.refresh(db_password)
    return db_password

@router.get("/", response_model=list[PasswordOut], summary="Получить все записи пользователя")
async def get_passwords(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import select
    result = await db.execute(
        select(PasswordEntry).where(PasswordEntry.owner_id == current_user.id)
    )
    return result.scalars().all()

@router.get("/{password_id}", response_model=PasswordOut, summary="Получить запись по ID")
async def get_password(
    password_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import select
    result = await db.execute(
        select(PasswordEntry).where(
            PasswordEntry.id == password_id,
            PasswordEntry.owner_id == current_user.id
        )
    )
    password = result.scalar_one_or_none()
    if not password:
        raise HTTPException(status_code=404, detail="Password not found")
    return password

@router.put("/{password_id}", response_model=PasswordOut, summary="Обновить запись")
async def update_password(
    password_id: int,
    update_data: PasswordUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import select
    result = await db.execute(
        select(PasswordEntry).where(
            PasswordEntry.id == password_id,
            PasswordEntry.owner_id == current_user.id
        )
    )
    password = result.scalar_one_or_none()
    if not password:
        raise HTTPException(status_code=404, detail="Password not found")

    if update_data.service:
        password.service = update_data.service
    if update_data.username:
        password.username = update_data.username
    if update_data.password:
        password.encrypted_password = encrypt_password(update_data.password)

    await db.commit()
    await db.refresh(password)
    return password

@router.delete("/{password_id}", summary="Удалить запись")
async def delete_password(
    password_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import select
    result = await db.execute(
        select(PasswordEntry).where(
            PasswordEntry.id == password_id,
            PasswordEntry.owner_id == current_user.id
        )
    )
    password = result.scalar_one_or_none()
    if not password:
        raise HTTPException(status_code=404, detail="Password not found")

    await db.delete(password)
    await db.commit()
    return {"detail": "Password deleted"}