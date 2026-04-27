"""
API Router — Machine Learning Endpoints
Prediksi kebutuhan air & level hidrasi menggunakan model ML.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
try:
    from app.services.ml_service import (
        predict_water_intake,
        predict_hydration_level,
        get_model_info,
        train_models,
    )
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

router = APIRouter(prefix="/api/ml", tags=["machine-learning"])


class PredictRequest(BaseModel):
    """Input untuk prediksi ML."""
    age:       int   = Field(..., ge=1, le=120, description="Usia pengguna")
    gender:    str   = Field(..., description="Jenis kelamin: male/female")
    weight_kg: float = Field(..., ge=10, le=300, description="Berat badan (kg)")
    activity:  str   = Field(..., description="Level aktivitas: low/moderate/high")
    weather:   str   = Field(..., description="Kondisi cuaca: cold/normal/hot")


class PredictResponse(BaseModel):
    """Response prediksi ML."""
    success: bool
    data: dict


@router.post("/predict", response_model=PredictResponse)
async def ml_predict(request: PredictRequest):
    """
    🔮 Prediksi kebutuhan air harian & level hidrasi berdasarkan ML model.
    
    Model dilatih dari 30.000+ data Daily_Water_Intake.csv menggunakan
    Random Forest (Regressor + Classifier).
    """
    if not ML_AVAILABLE:
        raise HTTPException(status_code=501, detail="ML features are disabled due to server constraints")
    
    try:
        # Prediksi intake air (liter)
        predicted_intake = predict_water_intake(
            age=request.age,
            gender=request.gender,
            weight_kg=request.weight_kg,
            activity=request.activity,
            weather=request.weather,
        )

        # Prediksi hydration level
        hydration = predict_hydration_level(
            age=request.age,
            gender=request.gender,
            weight_kg=request.weight_kg,
            activity=request.activity,
            weather=request.weather,
        )

        return {
            "success": True,
            "data": {
                "predicted_intake_liters": predicted_intake,
                "predicted_intake_ml": round(predicted_intake * 1000),
                "hydration_level": hydration["level"],
                "hydration_confidence": hydration["confidence"],
                "hydration_probabilities": hydration["probabilities"],
                "input_used": {
                    "age": request.age,
                    "gender": request.gender,
                    "weight_kg": request.weight_kg,
                    "activity": request.activity,
                    "weather": request.weather,
                },
            },
        }
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@router.post("/retrain")
async def ml_retrain():
    """
    🔄 Trigger re-training model dari dataset.
    Berguna jika dataset diperbarui.
    """
    if not ML_AVAILABLE:
        raise HTTPException(status_code=501, detail="ML features are disabled due to server constraints")
    
    try:
        metrics = train_models(force=True)
        return {
            "success": True,
            "message": "Model berhasil di-retrain!",
            "metrics": metrics,
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Dataset Daily_Water_Intake.csv tidak ditemukan di ml/data/",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training error: {str(e)}")


@router.get("/model-info")
async def ml_model_info():
    """
    📊 Lihat informasi model: apakah sudah di-train, metrics, dll.
    """
    if not ML_AVAILABLE:
        return {"success": False, "data": {"error": "ML disabled"}}
    
    info = get_model_info()
    return {
        "success": True,
        "data": info,
    }
