import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin

router = APIRouter(prefix="/api/auth", tags=["auth"])


def hash_password(password: str) -> str:
    """Hash password menggunakan bcrypt"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verifikasi password dengan hash"""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


@router.post("/register")
def register(data: UserRegister, db: Session = Depends(get_db)):
    """Registrasi user baru dengan username, password, dan data diri"""

    try:
        # Cek apakah username sudah dipakai
        existing = db.query(User).filter(User.username == data.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username sudah digunakan")

        # Buat user baru
        new_user = User(
            username=data.username,
            password_hash=hash_password(data.password),
            name=data.name,
            age=data.age,
            gender=data.gender.value,
            weight_kg=data.weight_kg,
            height_cm=data.height_cm,
            activity=data.activity.value,
            city=data.city or "Bandar Lampung",
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "success": True,
            "message": "Registrasi berhasil!",
            "data": {
                "id": new_user.id,
                "username": new_user.username,
                "name": new_user.name,
                "age": new_user.age,
                "gender": new_user.gender,
                "weight_kg": new_user.weight_kg,
                "height_cm": new_user.height_cm,
                "activity": new_user.activity,
                "city": new_user.city,
            },
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Login dengan username dan password"""

    user = db.query(User).filter(User.username == data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Username atau password salah")

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Username atau password salah")

    return {
        "success": True,
        "message": "Login berhasil!",
        "data": {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "age": user.age,
            "gender": user.gender,
            "weight_kg": user.weight_kg,
            "height_cm": user.height_cm,
            "activity": user.activity,
            "city": user.city,
        },
    }
