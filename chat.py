from supabase_client import supabase
from llm import chat_completion
from rag import get_relevant_context

def get_messages(chat_id):
    result = supabase.table("messages").select("role, content").eq("chat_id", chat_id).order("id").execute()
    return [(row["role"], row["content"]) for row in result.data]

def send_message(chat_id, user_input):
    # fetch history
    history = supabase.table("messages").select("role, content").eq("chat_id", chat_id).order("id").execute()
    texts = [c for r, c in [(row["role"], row["content"]) for row in history.data] if r == "user"]

    # RAG context
    context = get_relevant_context(texts, user_input)

    messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
    for ctx in context:
        messages.append({"role": "user", "content": ctx})
    messages.append({"role": "user", "content": user_input})

    reply = chat_completion(messages)

    # insert user + assistant messages
    supabase.table("messages").insert({
        "chat_id": chat_id,
        "role": "user",
        "content": user_input
    }).execute()

    supabase.table("messages").insert({
        "chat_id": chat_id,
        "role": "assistant",
        "content": reply
    }).execute()

    return reply