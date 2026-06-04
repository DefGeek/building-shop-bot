# app/web.py
from fastapi import FastAPI
from app.presentation.routers.auth import router as auth_router

app = FastAPI(title="СтройМаркет AI API")



# Подключаем наши роутеры
#prefix добавляет автоматически префикс к пути
#tags нужно для группировки автоматической документации по http://localhost:8000/docs
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}