from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

class WaterLogCreate(BaseModel):
    amount_ml: float = Field(..., ge=50, le=5000, description="Jumlah air dalam mL")
    log_date:  date  = Field(default_factory=date.today)
    note:      Optional[str] = None

class WaterLogResponse(WaterLogCreate):
    id:        int
    logged_at: datetime

    class Config:
        from_attributes = True

class DailySummary(BaseModel):
    date:          date
    total_ml:      float
    target_ml:     float
    percentage:    float
    logs:          List[WaterLogResponse]
    goal_met:      bool