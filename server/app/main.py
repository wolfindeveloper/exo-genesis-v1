# server/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# 👇 ИМПОРТ ОБЯЗАТЕЛЕН
from app.api import config, expeditions, lab, hangar

app = FastAPI(title="Exo Genesis API", version="0.1.0")

# 🔐 CORS: разрешаем запросы с фронтенда (Vercel, localhost, Telegram Webview)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для продакшена можно заменить на ["https://*.vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 👇 ПОДКЛЮЧЕНИЕ РОУТЕРОВ ОБЯЗАТЕЛЬНО
app.include_router(config.router)
app.include_router(expeditions.router)
app.include_router(lab.router) 
app.include_router(hangar.router)

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "exo-server"}