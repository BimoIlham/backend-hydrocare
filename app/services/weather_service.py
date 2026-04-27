import httpx
from app.core.config import settings

async def get_weather(city: str) -> dict:
    """
    Ambil data cuaca dari OpenWeather API.
    Menggunakan httpx async untuk performa lebih baik.
    """
    api_key = settings.openweather_api_key
    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q":     city,
        "appid": api_key,
        "units": "metric",  # Celsius
        "lang":  "id",      # Bahasa Indonesia
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        return {
            "city":        data["name"],
            "country":     data["sys"]["country"],
            "temperature": data["main"]["temp"],
            "feels_like":  data["main"]["feels_like"],
            "humidity":    data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "icon":        data["weather"][0]["icon"],
            "wind_speed":  data["wind"]["speed"],
            # Flag apakah cuaca panas (berguna untuk menyesuaikan target)
            "is_hot":      data["main"]["temp"] > 32,
        }
    except httpx.TimeoutException:
        # Kembalikan data default jika API timeout
        return _default_weather(city)
    except Exception as e:
        return _default_weather(city)

def _default_weather(city: str) -> dict:
    """Fallback jika OpenWeather tidak bisa diakses"""
    return {
        "city":        city,
        "country":     "ID",
        "temperature": 30.0,  # Asumsi panas untuk Lampung
        "feels_like":  33.0,
        "humidity":    75,
        "description": "tidak tersedia",
        "icon":        "01d",
        "wind_speed":  2.0,
        "is_hot":      True,
    }