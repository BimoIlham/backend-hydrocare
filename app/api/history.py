from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from app.core.database import get_db
from app.models.water_log import WaterLog, Badge
from app.schemas.water_log import WaterLogCreate, DailySummary
from datetime import date, timedelta
from typing import List

router = APIRouter(prefix="/api/history", tags=["history"])

@router.post("/log")
def add_water_log(log_data: WaterLogCreate, x_user_id: int = Header(None), db: Session = Depends(get_db)):
    """Catat konsumsi air baru"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="User ID tidak ditemukan")
    try:
        new_log = WaterLog(
            amount_ml=log_data.amount_ml,
            date=log_data.log_date,
            note=log_data.note,
            user_id=x_user_id
        )
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        return {"success": True, "data": new_log}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/daily/{date_str}")
def get_daily_summary(date_str: str, target_ml: float = 2000, x_user_id: int = Header(None), db: Session = Depends(get_db)):
    """
    Ambil ringkasan konsumsi air untuk satu hari tertentu.
    Format date_str: YYYY-MM-DD
    """
    try:
        query_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Format tanggal tidak valid. Gunakan YYYY-MM-DD")

    logs = db.query(WaterLog).filter(WaterLog.date == query_date, WaterLog.user_id == x_user_id).all()
    total_ml = sum(log.amount_ml for log in logs)
    percentage = (total_ml / target_ml * 100) if target_ml > 0 else 0

    return {
        "date":       date_str,
        "total_ml":   round(total_ml),
        "target_ml":  target_ml,
        "percentage": round(min(percentage, 100), 1),
        "goal_met":   total_ml >= target_ml,
        "logs":       logs,
    }

@router.get("/weekly")
def get_weekly_history(target_ml: float = 2000, x_user_id: int = Header(None), db: Session = Depends(get_db)):
    """Ambil histori 7 hari terakhir untuk grafik mingguan"""
    today = date.today()
    week_data = []

    for i in range(6, -1, -1):  # 6 hari lalu sampai hari ini
        query_date = today - timedelta(days=i)
        logs = db.query(WaterLog).filter(WaterLog.date == query_date, WaterLog.user_id == x_user_id).all()
        total = sum(log.amount_ml for log in logs)

        week_data.append({
            "date":     query_date.isoformat(),
            "day_name": _get_day_name(query_date),
            "total_ml": round(total),
            "goal_met": total >= target_ml,
        })

    return {"success": True, "data": week_data}

@router.delete("/log/{log_id}")
def delete_log(log_id: int, x_user_id: int = Header(None), db: Session = Depends(get_db)):
    """Hapus satu entry log"""
    log = db.query(WaterLog).filter(WaterLog.id == log_id, WaterLog.user_id == x_user_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log tidak ditemukan")
    db.delete(log)
    db.commit()
    return {"success": True, "message": "Log berhasil dihapus"}

def _get_day_name(d: date) -> str:
    """Konversi tanggal ke nama hari dalam bahasa Indonesia"""
    days = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
    return days[d.weekday()]