"""Debug: check actual table structure and test insert"""
from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Check column details
    result = conn.execute(text("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name='users' AND table_schema='public'
        ORDER BY ordinal_position
    """))
    print("=== users table columns ===")
    for row in result:
        print(f"  {row[0]}: {row[1]} | nullable={row[2]} | default={row[3]}")
    
    # Try a direct insert
    print("\n=== Testing direct insert ===")
    try:
        conn.execute(text("""
            INSERT INTO users (username, password_hash, name, age, gender, weight_kg, height_cm, activity, city)
            VALUES ('directtest', 'hash123', 'Direct Test', 25, 'male', 70, 170, 'moderate', 'Bandar Lampung')
        """))
        conn.commit()
        print("Direct insert SUCCESS!")
        # Clean up
        conn.execute(text("DELETE FROM users WHERE username='directtest'"))
        conn.commit()
        print("Cleanup done")
    except Exception as e:
        print(f"Direct insert FAILED: {e}")
        conn.rollback()
