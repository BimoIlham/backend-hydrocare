from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# Buat engine database — mendukung PostgreSQL (Supabase) dan SQLite
engine_args = {}
if "sqlite" in settings.database_url:
    engine_args["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL: set connection pool & timeout
    engine_args["pool_size"] = 5
    engine_args["max_overflow"] = 10
    engine_args["pool_timeout"] = 30
    engine_args["pool_recycle"] = 1800
    engine_args["pool_pre_ping"] = True
    engine_args["connect_args"] = {"connect_timeout": 10}

engine = create_engine(settings.database_url, **engine_args)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    """Base class untuk semua model SQLAlchemy"""
    pass

def get_db():
    """Dependency injection untuk database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()