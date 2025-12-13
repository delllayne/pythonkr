from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserOut
from app.auth import get_password_hash, create_access_token, verify_password, get_user_by_username

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, summary="Регистрация нового пользователя")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    existing = await db.execute(select(User).where(User.username == user.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already registered")

    db_user = User(username=user.username, hashed_password=get_password_hash(user.password))
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.post("/login", summary="Получение JWT токена")
async def login(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_username(db, user.username)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}