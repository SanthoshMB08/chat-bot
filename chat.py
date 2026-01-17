from database import conn
from llm import chat_completion
from rag import get_relevant_context

def get_messages(chat_id):
    return conn.execute(
        "SELECT role, content FROM messages WHERE chat_id=?",
        (chat_id,)
    ).fetchall()

def send_message(chat_id, user_input):
    history = conn.execute(
        "SELECT role, content FROM messages WHERE chat_id=?",
        (chat_id,)
    ).fetchall()

    texts = [c for r, c in history if r == "user"]
    context = get_relevant_context(texts, user_input)

    messages = [{"role": "system", "content": "You are a helpful AI assistant."}]

    for ctx in context:
        messages.append({"role": "user", "content": ctx})

    messages.append({"role": "user", "content": user_input})

    reply = chat_completion(messages)

    conn.execute(
        "INSERT INTO messages VALUES (NULL, ?, ?, ?, NULL)",
        (chat_id, "user", user_input)
    )
    conn.execute(
        "INSERT INTO messages VALUES (NULL, ?, ?, ?, NULL)",
        (chat_id, "assistant", reply)
    )
    conn.commit()

    return reply
