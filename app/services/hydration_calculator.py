"""
Kalkulator kebutuhan air — HydroCare (Multiplier System)
Formula disesuaikan untuk iklim tropis Indonesia.

Final Intake = Base × Faktor Total

Referensi:
- WHO: 35 mL/kg berat badan
- Kemenkes RI: Pria dewasa 2.5-3.0 liter/hari
- Penyesuaian proporsional (bukan additive) agar hasil tetap realistis
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class HydrationInput:
    weight_kg:    float
    age:          int
    gender:       str    # "male" / "female"
    activity:     str    # "light" / "moderate" / "heavy"
    temperature:  Optional[float] = 25.0   # Suhu dalam Celsius
    humidity:     Optional[float] = None    # Kelembapan dalam %


@dataclass
class HydrationResult:
    base_ml:        float    # Kebutuhan dasar (berat × 35)
    gender_ml:      float    # Tambahan gender (sebagai mL)
    age_ml:         float    # Koreksi usia (sebagai mL, bisa negatif)
    activity_ml:    float    # Tambahan aktivitas (sebagai mL)
    weather_ml:     float    # Tambahan cuaca (sebagai mL)
    humidity_ml:    float    # Tambahan kelembapan (sebagai mL)
    total_ml:       float    # Total rekomendasi
    total_liters:   float
    reminder_hours: int      # Seberapa sering reminder (jam)
    # Faktor detail (untuk transparansi)
    factor_activity:  float
    factor_weather:   float
    factor_humidity:  float
    factor_total:     float


def calculate_daily_water(data: HydrationInput) -> HydrationResult:
    """
    Rumus Multiplier (disesuaikan untuk Indonesia):

    1. Base       = berat_badan × 35 mL  (standar WHO)
    2. Gender     = pria +300 mL, wanita +0 (flat, bukan multiplier)
    3. Usia       = anak (×0.8), lansia (×0.9), dewasa (×1.0)
    4. Faktor multiplier (proporsional terhadap base):
       - Aktivitas:
         · Ringan:  ×1.00 (+0%)  — kerja kantor, minim keringat
         · Sedang:  ×1.10 (+10%) — olahraga 2-3x/minggu
         · Berat:   ×1.20 (+20%) — olahraga intensif harian
       - Cuaca (iklim tropis Indonesia):
         · < 25°C:  ×1.00 (+0%)  — sejuk, jarang di Indonesia
         · 25-30°C: ×1.05 (+5%)  — tropis normal
         · 30-35°C: ×1.10 (+10%) — panas khas siang
         · > 35°C:  ×1.15 (+15%) — sangat panas
       - Kelembapan:
         · ≤ 70%:   ×1.00 (+0%)
         · > 70%:   ×1.03 (+3%)
         · > 80%:   ×1.05 (+5%)
         · > 90%:   ×1.08 (+8%)

    Contoh: Bimo 70kg pria, ringan, 31°C, humidity 65%
      Base   = 2450 + 300 (gender) = 2750
      Faktor = 1.00 (ringan) + 0.10 (31°C) + 0.00 (humidity 65%) = 1.10
      Total  = 2750 × 1.10 = 3025 mL ✅ (sesuai Kemenkes 2.5-3.0 L)
    """

    # ─── 1. Kebutuhan dasar (mL) ───
    raw_base = data.weight_kg * 35

    # ─── 2. Koreksi gender (flat, bukan multiplier) ───
    gender_ml = 300 if data.gender == "male" else 0

    # ─── 3. Koreksi usia ───
    if data.age < 14:
        age_factor = 0.8
    elif data.age > 65:
        age_factor = 0.9
    else:
        age_factor = 1.0

    adjusted_base = (raw_base * age_factor) + gender_ml
    age_ml = round(raw_base * age_factor - raw_base)

    # ─── 4. Faktor aktivitas ───
    activity_factors = {
        "light":    0.00,   # Kerja kantor → tidak ada tambahan
        "moderate": 0.10,   # Olahraga rutin → +10%
        "heavy":    0.20,   # Atlet → +20%
    }
    f_activity = activity_factors.get(data.activity, 0.00)

    # ─── 5. Faktor cuaca (proporsional, khusus tropis) ───
    temp = data.temperature or 25
    if temp < 25:
        f_weather = 0.00
    elif temp < 30:
        f_weather = 0.05    # Tropis normal
    elif temp < 35:
        f_weather = 0.10    # Panas khas siang Indonesia
    else:
        f_weather = 0.15    # Sangat panas

    # ─── 6. Faktor kelembapan ───
    humidity = data.humidity or 0
    if humidity > 90:
        f_humidity = 0.08
    elif humidity > 80:
        f_humidity = 0.05
    elif humidity > 70:
        f_humidity = 0.03
    else:
        f_humidity = 0.00

    # ─── Hitung total ───
    f_total = 1.0 + f_activity + f_weather + f_humidity
    total_ml = adjusted_base * f_total

    # Hitung mL per komponen (untuk breakdown UI)
    activity_ml = round(adjusted_base * f_activity)
    weather_ml  = round(adjusted_base * f_weather)
    humidity_ml = round(adjusted_base * f_humidity)

    # ─── Seberapa sering reminder ───
    if temp > 32 or data.activity == "heavy":
        reminder_hours = 1
    elif data.activity == "moderate":
        reminder_hours = 1.5
    else:
        reminder_hours = 2

    return HydrationResult(
        base_ml=round(raw_base),
        gender_ml=round(gender_ml),
        age_ml=round(age_ml),
        activity_ml=round(activity_ml),
        weather_ml=round(weather_ml),
        humidity_ml=round(humidity_ml),
        total_ml=round(total_ml),
        total_liters=round(total_ml / 1000, 2),
        reminder_hours=int(reminder_hours),
        factor_activity=f_activity,
        factor_weather=f_weather,
        factor_humidity=f_humidity,
        factor_total=round(f_total, 2),
    )