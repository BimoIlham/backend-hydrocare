"""Script to add username and password_hash columns to existing users table"""
from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Check existing columns
    result = conn.execute(text(
        "SELECT column_name FROM information_schema.columns WHERE table_name='users'"
    ))
    cols = [r[0] for r in result]
    print("Existing columns:", cols)

    if "username" not in cols:
        conn.execute(text("ALTER TABLE users ADD COLUMN username VARCHAR(50)"))
        print("Added username column")
    else:
        print("username column already exists")

    if "password_hash" not in cols:
        conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(200)"))
        print("Added password_hash column")
    else:
        print("password_hash column already exists")

    # Create unique index on username
    try:
        conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users(username)"))
        print("Username index created/verified")
    except Exception as e:
        print(f"Index note: {e}")

    conn.commit()
    print("Migration complete!")
