# renderfix
import sys
if sys.version_info >= (3, 13):
    import typing
    # Фикс для SQLAlchemy в Python 3.13
    if not hasattr(typing, 'TypingOnly'):
        class TypingOnly: pass
        typing.TypingOnly = TypingOnly
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..models import User
from ..schemas import UserAdminCreate, UserOut
from ..auth import get_current_admin, get_password_hash

router = APIRouter(prefix="/admin", tags=["admin"])



@router.get("/users", response_model=list[UserOut], summary="Получить всех пользователей")
async def get_all_users(
        db: AsyncSession = Depends(get_db),
        current_admin=Depends(get_current_admin)
):
    from sqlalchemy import select
    result = await db.execute(select(User))
    return result.scalars().all()


# POST: Создать админа (только первый раз)
@router.post("/users", response_model=UserOut, summary="Создать администратора")
async def create_admin(
        user: UserAdminCreate,
        db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import select
    admin_exists = await db.execute(select(User).where(User.is_admin == True))
    if admin_exists.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Администратор уже существует")

    db_user = User(
        username=user.username,
        hashed_password=get_password_hash(user.password),
        is_admin=True
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


# DELETE: Удалить пользователя
@router.delete("/users/{user_id}", summary="Удалить пользователя")
async def delete_user(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_admin=Depends(get_current_admin)
):
    from sqlalchemy import select
    if current_admin.id == user_id:
        raise HTTPException(status_code=400, detail="Нельзя удалить свой аккаунт")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    from ..models import PasswordEntry
    await db.execute(
        PasswordEntry.__table__.delete().where(PasswordEntry.owner_id == user_id)
    )
    await db.delete(user)
    await db.commit()
    return {"detail": f"Пользователь {user.username} удалён"}