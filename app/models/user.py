from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    """
    Model untuk profil pengguna.
    auth_user_id = UUID dari Supabase Auth (unik per akun).
    """
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(200), nullable=False)
    name          = Column(String(100), nullable=False)
    age           = Column(Integer, nullable=False)
    gender        = Column(String(10), nullable=False)
    weight_kg     = Column(Float, nullable=False)
    height_cm     = Column(Float, nullable=False)
    activity      = Column(String(20), nullable=False)
    city          = Column(String(100), default="Bandar Lampung")
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), onupdate=func.now())