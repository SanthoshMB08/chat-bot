from database import conn

def add_prompt(project_id, title, content):
    conn.execute(
        "INSERT INTO prompts (project_id, title, content) VALUES (?, ?, ?)",
        (project_id, title, content)
    )
    conn.commit()

def get_prompts(project_id):
    return conn.execute(
        "SELECT title, content FROM prompts WHERE project_id=?",
        (project_id,)
    ).fetchall()
