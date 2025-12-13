from fastapi import FastAPI
from app.routers import passwords, auth
from app.database import Base, engine

app = FastAPI(
    title="Password Manager API",
    description="API для безопасного хранения паролей с JWT-аутентификацией и шифрованием",
    version="1.0.0"
)

@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(auth.router)
app.include_router(passwords.router)