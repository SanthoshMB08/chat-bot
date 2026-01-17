import bcrypt
from database import conn

def signup(email, password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        cur = conn.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, hashed)
        )
        conn.commit()
        return cur.lastrowid
    except:
        return None

def login(email, password):
    user = conn.execute(
        "SELECT id, password FROM users WHERE email=?",
        (email,)
    ).fetchone()

    if not user:
        return None

    user_id, hashed = user

    if bcrypt.checkpw(password.encode(), hashed):
        return user_id

    return None
