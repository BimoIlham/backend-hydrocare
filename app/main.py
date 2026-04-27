import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import hydration, history, user, weather, ml, auth, chat

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# Buat semua tabel di database (skip jika sudah ada, misal di Supabase)
try:
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables ready")
except Exception as e:
    logger.warning(f"⚠️ create_all skipped: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup & shutdown events."""
    # ── Startup ──
    logger.info("🚀 HydroCare API starting up...")

    # Auto-train ML model saat startup (jika belum ada)
    try:
        from app.services.ml_service import train_models
        logger.info("🤖 Checking ML models...")
        metrics = train_models(force=False)
        if metrics:
            r2 = metrics.get("regressor", {}).get("r2_score", "N/A")
            acc = metrics.get("classifier", {}).get("accuracy", "N/A")
            logger.info(f"   📊 Regressor R²: {r2} | Classifier Accuracy: {acc}")
        logger.info("✅ ML models ready!")
    except Exception as e:
        logger.warning(f"⚠️  ML model loading gagal: {e}. ML endpoint tetap tersedia, jalankan /api/ml/retrain.")

    yield

    # ── Shutdown ──
    logger.info("👋 HydroCare API shutting down...")


app = FastAPI(
    title="HydroCare API",
    description="Backend untuk aplikasi monitoring hidrasi tubuh dengan ML prediction",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — izinkan frontend React mengakses API
origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]
logger.info(f"🌐 CORS allowed origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Daftarkan semua router
app.include_router(auth.router)
app.include_router(hydration.router)
app.include_router(history.router)
app.include_router(user.router)
app.include_router(weather.router)
app.include_router(ml.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {
        "app":     "HydroCare API",
        "status":  "running",
        "version": "2.0.0",
        "ml":      "enabled",
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}