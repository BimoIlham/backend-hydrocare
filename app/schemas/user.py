from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class GenderEnum(str, Enum):
    male   = "male"
    female = "female"

class ActivityEnum(str, Enum):
    light    = "light"     # Aktivitas ringan (kerja kantoran)
    moderate = "moderate"  # Aktivitas sedang (jalan kaki, olahraga 3x/minggu)
    heavy    = "heavy"     # Aktivitas berat (atlet, kerja fisik)

# ── Auth Schemas ──

class UserRegister(BaseModel):
    """Schema untuk registrasi user baru"""
    username:  str          = Field(..., min_length=3, max_length=50)
    password:  str          = Field(..., min_length=6, max_length=100)
    name:      str          = Field(..., min_length=1, max_length=100)
    age:       int          = Field(..., ge=1, le=120)
    gender:    GenderEnum
    weight_kg: float        = Field(..., ge=10, le=300)
    height_cm: float        = Field(..., ge=50, le=250)
    activity:  ActivityEnum
    city:      Optional[str] = "Bandar Lampung"

class UserLogin(BaseModel):
    """Schema untuk login"""
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)

# ── Existing Schemas (backward compatible) ──

class UserCreate(BaseModel):
    name:      str         = Field(..., min_length=1, max_length=100)
    age:       int         = Field(..., ge=1, le=120)
    gender:    GenderEnum
    weight_kg: float       = Field(..., ge=10, le=300)
    height_cm: float       = Field(..., ge=50, le=250)
    activity:  ActivityEnum
    city:      Optional[str] = "Bandar Lampung"

class UserResponse(UserCreate):
    id:         int
    username:   Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True  # Izinkan konversi dari SQLAlchemy model