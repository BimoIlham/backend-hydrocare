"""Check water_logs schema"""
from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name='water_logs' AND table_schema='public'
        ORDER BY ordinal_position
    """))
    print("=== water_logs ===")
    for row in result:
        print(f"  {row[0]}: {row[1]} | nullable={row[2]}")

    result = conn.execute(text("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name='badges' AND table_schema='public'
        ORDER BY ordinal_position
    """))
    print("\n=== badges ===")
    for row in result:
        print(f"  {row[0]}: {row[1]} | nullable={row[2]}")
