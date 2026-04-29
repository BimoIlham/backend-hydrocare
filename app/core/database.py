from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

from sqlalchemy.pool import NullPool

# Buat engine database — mendukung PostgreSQL (Supabase) dan SQLite
engine_args = {}
if "sqlite" in settings.database_url:
    engine_args["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL: Gunakan NullPool karena Supabase port 6543 menggunakan PgBouncer (Transaction Mode)
    # Menggunakan pool_size bawaan SQLAlchemy dengan PgBouncer akan menyebabkan silent drop/rollback!
    engine_args["poolclass"] = NullPool
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