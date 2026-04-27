from sqlalchemy import Column, Integer, Float, DateTime, String, Date
from sqlalchemy.sql import func
from app.core.database import Base

class WaterLog(Base):
    """
    Setiap record = satu kali minum air.
    auth_user_id = UUID dari Supabase Auth.
    """
    __tablename__ = "water_logs"

    id            = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, index=True) # References users.id
    amount_ml     = Column(Float, nullable=False)
    date          = Column(Date, nullable=False)
    logged_at     = Column(DateTime(timezone=True), server_default=func.now())
    note          = Column(String(200), nullable=True)

class Badge(Base):
    """Badge yang sudah diraih user"""
    __tablename__ = "badges"

    id            = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, index=True) # References users.id
    badge_id      = Column(String(50))
    earned_at     = Column(DateTime(timezone=True), server_default=func.now())