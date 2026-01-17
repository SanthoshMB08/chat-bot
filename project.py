from supabase_client import supabase

def create_project(user_id, name, description=""):
    result = supabase.table("projects").insert({
        "user_id": user_id,
        "name": name,
        "description": description
    }).execute()
    return result.data[0]["id"]

def get_projects(user_id):
    result = supabase.table("projects").select("id, name").eq("user_id", user_id).order("id", desc=True).execute()
    return [(row["id"], row["name"]) for row in result.data]