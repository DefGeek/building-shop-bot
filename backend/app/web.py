from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.presentation.routers.auth import router as auth_router

app = FastAPI(title="СтройМаркет AI API")

# Подключаем наши роутеры
#prefix добавляет автоматически префикс к пути
#tags нужно для группировки автоматической документации по http://localhost:8000/docs
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])

# Раздаем статические файлы (HTML, JS, CSS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Главная страница - отдаем index.html
@app.get("/")
async def root():
    return FileResponse("app/static/index.html")

@app.get("/health")
async def health_check():
    return {"status": "ok"}