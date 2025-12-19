from fastapi import FastAPI
from starlette.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .routers import passwords, auth, admin  # ← добавлен admin
from .database import Base, engine

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Password Manager API",
    description="API для безопасного хранения паролей с JWT-аутентификацией и шифрованием",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    print(f"⚠️  Папка static не найдена: {static_dir}")

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/static/index.html")

app.include_router(auth.router)
app.include_router(passwords.router)
app.include_router(admin.router)  # ← новая строка