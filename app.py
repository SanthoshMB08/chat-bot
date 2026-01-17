import streamlit as st
from database import conn, init_db
from project import create_project, get_projects
from auth import login, signup
from chat import send_message, get_messages
from streamlit_cookies_manager import EncryptedCookieManager

# -------------- INIT DB ----------------
init_db()


# ---------------- COOKIE MANAGER ----------------
cookies = EncryptedCookieManager(
    prefix="ai_chat_app",   # unique prefix for your app
    password="supersecret"  # change this to a strong secret
)

if not cookies.ready():
    st.stop()

# ---------------- SESSION STATE ----------------
if "user_id" not in st.session_state:
    # try to restore from cookie
    if "user_id" in cookies:
        st.session_state.user_id = int(cookies["user_id"])
    else:
        st.session_state.user_id = None

if "project_id" not in st.session_state:
    st.session_state.project_id = None

if "chat_id" not in st.session_state:
    st.session_state.chat_id = None


# ---------------- AUTH UI ----------------
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
                cookies["user_id"] = str(uid)   # save to cookie
                cookies.save()
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
                cookies["user_id"] = str(uid)   # save to cookie
                cookies.save()
                st.rerun()
            else:
                st.error("User already exists")

    st.stop()

# -------------- SIDEBAR: PROJECTS + CHATS -------------
st.sidebar.title("🧠 Workspace")

# -- Projects
projects = get_projects(st.session_state.user_id)

for pid, pname in projects:

    # project header + delete
    colp1, colp2 = st.sidebar.columns([8, 1])

    if colp1.button(f"📁 {pname}", key=f"proj-{pid}"):
        st.session_state.project_id = pid
        st.session_state.chat_id = None
        st.rerun()

    if colp2.button("🗑", key=f"del-proj-{pid}"):
        # delete all messages in all chats in this project
        conn.execute("""
            DELETE FROM messages 
            WHERE chat_id IN (SELECT id FROM chats WHERE project_id=?)
        """, (pid,))

        conn.execute("DELETE FROM chats WHERE project_id=?", (pid,))
        conn.execute("DELETE FROM projects WHERE id=?", (pid,))
        conn.commit()

        if st.session_state.project_id == pid:
            st.session_state.project_id = None
            st.session_state.chat_id = None

        st.rerun()

    # only show chats when project is active
    if st.session_state.project_id == pid:

        # fetch chats for this project
        chat_rows = conn.execute(
            "SELECT id, title FROM chats WHERE project_id=? ORDER BY id DESC",
            (pid,)
        ).fetchall()

        for cid, ctitle in chat_rows:
            c1, c2 = st.sidebar.columns([8, 1])

            if c1.button(f"   💬 {ctitle}", key=f"chat-{pid}-{cid}"):
                st.session_state.chat_id = cid
                st.rerun()

            if c2.button("🗑", key=f"del-chat-{pid}-{cid}"):
                conn.execute("DELETE FROM messages WHERE chat_id=?", (cid,))
                conn.execute("DELETE FROM chats WHERE id=?", (cid,))
                conn.commit()

                if st.session_state.chat_id == cid:
                    st.session_state.chat_id = None

                st.rerun()

        # new chat inside this project
        if st.sidebar.button("➕ New Chat", key=f"new-chat-{pid}"):
            cur = conn.execute(
                "INSERT INTO chats (user_id, project_id, title) VALUES (?, ?, ?)",
                (st.session_state.user_id, pid, "New Chat")
            )
            st.session_state.chat_id = cur.lastrowid
            conn.commit()
            st.rerun()

    st.sidebar.markdown("---")

# add new project UI
st.sidebar.subheader("➕ New Project")
new_project = st.sidebar.text_input("Project name")
if st.sidebar.button("Create Project"):
    if new_project:
        pid = create_project(st.session_state.user_id, new_project)
        st.session_state.project_id = pid
        st.session_state.chat_id = None
        st.rerun()
# logout button
if st.sidebar.button("🚪 Logout"):
    st.session_state.clear()
    cookies["user_id"] = ""   # clear cookie
    cookies.save()
    st.rerun()


# ---------- MAIN CHAT UI ----------------
# ensure chat_id exists before showing
if st.session_state.chat_id is None:
    st.info("Select a chat from the sidebar or create a new one!")
    st.stop()

st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

messages = get_messages(st.session_state.chat_id)
for role, content in messages:
    css_class = "user" if role == "user" else "assistant"
    st.markdown(
        f"<div class='message {css_class}'>{content}</div>",
        unsafe_allow_html=True
    )

st.markdown("</div>", unsafe_allow_html=True)

# ---------- INPUT BOX -------------
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Message", key="input")
    send = st.form_submit_button("Send")

if send and user_input:
    send_message(st.session_state.chat_id, user_input)

    conn.execute(
        "UPDATE chats SET title=? WHERE id=? AND title='New Chat'",
        (user_input[:30], st.session_state.chat_id)
    )
    conn.commit()
    st.rerun()
