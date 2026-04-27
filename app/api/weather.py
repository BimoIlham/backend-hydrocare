from fastapi import APIRouter
from app.services.weather_service import get_weather
from app.core.config import settings

router = APIRouter(prefix="/api/weather", tags=["weather"])

@router.get("/{city}")
async def fetch_weather(city: str):
    """Ambil data cuaca untuk kota tertentu"""
    weather = await get_weather(city)
    return {"success": True, "data": weather}

@router.get("/")
async def fetch_default_weather():
    """Ambil cuaca untuk kota default (Bandar Lampung)"""
    weather = await get_weather(settings.city_default)
    return {"success": True, "data": weather}