from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/api/user", tags=["user"])

@router.get("/profile")
def get_profile(db: Session = Depends(get_db)):
    """Ambil profil user (selalu hanya 1 user)"""
    user = db.query(User).first()
    if not user:
        return {"exists": False, "data": None}
    return {"exists": True, "data": user}

@router.post("/profile")
def create_or_update_profile(user_data: UserCreate, db: Session = Depends(get_db)):
    """Buat profil baru atau update profil yang ada"""
    existing = db.query(User).first()

    if existing:
        # Update profil yang ada
        for field, value in user_data.model_dump().items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return {"success": True, "message": "Profil diperbarui", "data": existing}
    else:
        # Buat profil baru
        new_user = User(**user_data.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"success": True, "message": "Profil dibuat", "data": new_user}