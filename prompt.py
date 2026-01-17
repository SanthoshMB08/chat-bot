from supabase_client import supabase

def add_prompt(project_id, title, content):
    supabase.table("prompts").insert({
        "project_id": project_id,
        "title": title,
        "content": content
    }).execute()

def get_prompts(project_id):
    result = supabase.table("prompts").select("title, content").eq("project_id", project_id).execute()
    return [(row["title"], row["content"]) for row in result.data]