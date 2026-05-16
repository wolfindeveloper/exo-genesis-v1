# server/app/api/config.py
from fastapi import APIRouter
from pathlib import Path
import yaml
from functools import lru_cache

router = APIRouter(prefix="/api/config", tags=["config"])

# === Надёжный поиск папки data/ в корне проекта ===
def find_data_dir() -> Path:
    current = Path(__file__).resolve()
    # Поднимаемся вверх, ищем папку "data"
    for _ in range(5):
        candidate = current.parent / "data"
        if candidate.exists() and (candidate / "zones.yaml").exists():
            return candidate
        current = current.parent
        if current.parent == current:  # достигли корня диска
            break
    # Fallback: проект-рут через env-переменную или cwd
    return Path.cwd() / "data"

DATA_DIR = find_data_dir()

# Для отладки (раскомментируй при необходимости)
# print(f"🔍 DATA_DIR: {DATA_DIR}")
# print(f"🔍 zones.yaml exists: {(DATA_DIR / 'zones.yaml').exists()}")

@lru_cache(maxsize=1)
def load_yaml(filename: str):
    """Кэшированная загрузка YAML"""
    path = DATA_DIR / filename
    if not path.exists():
        print(f"⚠️ File not found: {path}")
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        print(f"❌ Error loading {filename}: {e}")
        return []

@router.get("/zones")
def get_zones():
    return load_yaml("zones.yaml")

@router.get("/ships")
def get_ships():
    return load_yaml("ships.yaml")

@router.get("/artifacts")
def get_artifacts():
    return load_yaml("artifacts.yaml")