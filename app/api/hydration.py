from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserCreate
from app.services.hydration_calculator import HydrationInput, calculate_daily_water
from app.services.weather_service import get_weather
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/hydration", tags=["hydration"])

class HydrationRequest(BaseModel):
    weight_kg:   float
    age:         int
    gender:      str
    activity:    str
    city:        Optional[str] = "Bandar Lampung"
    temperature: Optional[float] = None  # Jika None, ambil dari API cuaca
    humidity:    Optional[float] = None   # Jika None, ambil dari API cuaca

@router.post("/calculate")
async def calculate_hydration(request: HydrationRequest):
    """
    Endpoint utama: hitung kebutuhan air harian.
    Mengembalikan hasil rule-based DAN prediksi ML.
    Sekarang termasuk breakdown lengkap: base + gender + age + activity + cuaca + humidity.
    """
    temperature = request.temperature
    humidity = request.humidity

    # Jika suhu/humidity tidak diberikan, ambil dari cuaca otomatis
    if temperature is None or humidity is None:
        weather = await get_weather(request.city)
        if temperature is None:
            temperature = weather["temperature"]
        if humidity is None:
            humidity = weather.get("humidity", 65)
    
    # ── 1. Rule-based calculation (Hybrid System) ──
    hydration_input = HydrationInput(
        weight_kg=request.weight_kg,
        age=request.age,
        gender=request.gender,
        activity=request.activity,
        temperature=temperature,
        humidity=humidity,
    )
    result = calculate_daily_water(hydration_input)

    # ── 2. ML prediction ──
    ml_prediction = None
    try:
        from app.services.ml_service import predict_water_intake, predict_hydration_level

        # Map temperature ke weather category untuk ML
        if temperature >= 30:
            weather_cat = "hot"
        elif temperature >= 20:
            weather_cat = "normal"
        else:
            weather_cat = "cold"

        predicted_intake = predict_water_intake(
            age=request.age,
            gender=request.gender,
            weight_kg=request.weight_kg,
            activity=request.activity,
            weather=weather_cat,
        )
        hydration_level = predict_hydration_level(
            age=request.age,
            gender=request.gender,
            weight_kg=request.weight_kg,
            activity=request.activity,
            weather=weather_cat,
        )

        ml_prediction = {
            "predicted_intake_liters": predicted_intake,
            "predicted_intake_ml": round(predicted_intake * 1000),
            "hydration_level": hydration_level["level"],
            "hydration_confidence": hydration_level["confidence"],
        }
    except Exception as e:
        logger.warning(f"ML prediction gagal: {e}")
        ml_prediction = {"error": "ML model belum tersedia", "detail": str(e)}

    return {
        "success": True,
        "data": {
            "rule_based": {
                "base_ml":        result.base_ml,
                "gender_ml":      result.gender_ml,
                "age_ml":         result.age_ml,
                "activity_ml":    result.activity_ml,
                "weather_ml":     result.weather_ml,
                "humidity_ml":    result.humidity_ml,
                "total_ml":       result.total_ml,
                "total_liters":   result.total_liters,
                "reminder_hours": result.reminder_hours,
                "factor_activity": result.factor_activity,
                "factor_weather":  result.factor_weather,
                "factor_humidity": result.factor_humidity,
                "factor_total":    result.factor_total,
            },
            "ml_prediction": ml_prediction,
            "temperature_used": temperature,
            "humidity_used": humidity,
        }
    }