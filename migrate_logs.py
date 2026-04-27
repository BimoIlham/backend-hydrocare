"""Script to add user_id to water_logs and badges"""
from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Check water_logs
    result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='water_logs' AND table_schema='public'"))
    cols = [r[0] for r in result]
    print("water_logs columns:", cols)

    if "user_id" not in cols:
        conn.execute(text("ALTER TABLE water_logs ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE"))
        print("Added user_id to water_logs")
    else:
        print("user_id already exists in water_logs")

    # Check badges
    result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='badges' AND table_schema='public'"))
    cols = [r[0] for r in result]
    if "user_id" not in cols:
        conn.execute(text("ALTER TABLE badges ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE"))
        print("Added user_id to badges")
    else:
        print("user_id already exists in badges")

    conn.commit()
    print("Migration complete!")
