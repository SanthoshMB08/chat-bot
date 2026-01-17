from database import conn

def create_project(user_id, name, description=""):
    cur = conn.execute(
        "INSERT INTO projects (user_id, name, description) VALUES (?, ?, ?)",
        (user_id, name, description)
    )
    conn.commit()
    return cur.lastrowid

def get_projects(user_id):
    return conn.execute(
        "SELECT id, name FROM projects WHERE user_id=? ORDER BY id DESC",
        (user_id,)
    ).fetchall()
