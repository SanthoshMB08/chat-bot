import streamlit as st
from database import conn, init_db
from project import create_project, get_projects
# ---------- INIT DB ----------
init_db()

# ---------- SESSION STATE ----------
if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "chat_id" not in st.session_state:
    st.session_state.chat_id = None
if "project_id" not in st.session_state:
    st.session_state.project_id = None

# ---------- AUTH ----------
from auth import login, signup
from chat import send_message, get_messages

# ---------- AUTH UI ----------
if st.session_state.user_id is None:
    st.title("🔐 AI Chat Login")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            uid = login(email, password)
            if uid:
                st.session_state.user_id = uid
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        email = st.text_input("Email", key="s_email")
        password = st.text_input("Password", type="password", key="s_pass")

        if st.button("Signup"):
            uid = signup(email, password)
            if uid:
                st.session_state.user_id = uid
                st.rerun()
            else:
                st.error("User already exists")

    st.stop()

# ---------- DARK MODE ----------
dark = st.sidebar.toggle("🌙 Dark mode")

if dark:
    st.markdown("""
    <style>
    body { background:#0f172a; color:white }
    </style>
    """, unsafe_allow_html=True)

# ---------- SIDEBAR ----------
st.sidebar.title("💬 Chats")

if st.sidebar.button("+ New Chat"):
    cur = conn.execute(
        "INSERT INTO chats (user_id, title) VALUES (?, ?)",
        (st.session_state.user_id, "New Chat")
    )
    st.session_state.chat_id = cur.lastrowid
    conn.commit()
    st.rerun()

    # ---------- LOAD CHAT LIST ----------
chats = conn.execute(
    "SELECT id, title FROM chats WHERE user_id=? ORDER BY id DESC",
    (st.session_state.user_id,)
).fetchall()

if not chats:
    cur = conn.execute(
        "INSERT INTO chats (user_id, title) VALUES (?, ?)",
        (st.session_state.user_id, "New Chat")
    )
    st.session_state.chat_id = cur.lastrowid
    conn.commit()
else:
    if st.session_state.chat_id is None:
        st.session_state.chat_id = chats[0][0]

for cid, title in chats:
    if st.sidebar.button(title, key=f"chat-{cid}"):
        st.session_state.chat_id = cid
        st.rerun()
st.sidebar.title("🧠 Workspace")

projects = get_projects(st.session_state.user_id)

for pid, pname in projects:

    # ---------- PROJECT HEADER ----------
    if st.sidebar.button(f"📁 {pname}", key=f"proj-{pid}"):
        st.session_state.project_id = pid
        st.session_state.chat_id = None
        st.rerun()

    # ---------- SHOW CHATS ONLY FOR ACTIVE PROJECT ----------
    if st.session_state.project_id == pid:

        chats = conn.execute(
            "SELECT id, title FROM chats WHERE project_id=? ORDER BY id DESC",
            (pid,)
        ).fetchall()

        for cid, title in chats:
            if st.sidebar.button(f"   💬 {title}", key=f"chat-{pid}-{cid}-project"):
                st.session_state.chat_id = cid
                st.rerun()

        # ---------- NEW CHAT UNDER PROJECT ----------
        if st.sidebar.button("➕ New Chat", key=f"new-chat-{pid}"):
            cur = conn.execute(
                "INSERT INTO chats (user_id, project_id, title) VALUES (?, ?, ?)",
                (st.session_state.user_id, pid, "New Chat")
            )
            st.session_state.chat_id = cur.lastrowid
            conn.commit()
            st.rerun()

    st.sidebar.markdown("---")

# ---------- CREATE NEW PROJECT ----------
st.sidebar.subheader("➕ New Project")

new_project = st.sidebar.text_input("Project name")

if st.sidebar.button("Create Project"):
    if new_project:
        pid = create_project(st.session_state.user_id, new_project)
        st.session_state.project_id = pid
        st.session_state.chat_id = None
        st.rerun()


# ---------- LOGOUT ----------
if st.sidebar.button("🚪 Logout"):
    st.session_state.user_id = None
    st.session_state.chat_id = None
    st.rerun()

# ---------- CHAT UI ----------
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

messages = get_messages(st.session_state.chat_id)

for role, content in messages:
    css_class = "user" if role == "user" else "assistant"
    st.markdown(
        f"<div class='message {css_class}'>{content}</div>",
        unsafe_allow_html=True
    )

st.markdown("</div>", unsafe_allow_html=True)


# ---------- INPUT ----------
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Message")
    send = st.form_submit_button("Send")

if send and user_input:
    send_message(st.session_state.chat_id, user_input)

    conn.execute(
        "UPDATE chats SET title=? WHERE id=? AND title='New Chat'",
        (user_input[:30], st.session_state.chat_id)
    )
    conn.commit()
    st.rerun()
