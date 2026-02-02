import streamlit as st
from project import create_project, get_projects
from auth import login, signup, is_valid_uuid
from chat import send_message, get_messages
from supabase_client import supabase
from streamlit_cookies_manager import CookieManager



#  COOKIE SETUP FOR LOGIN 
cookies = CookieManager(prefix="ai_chat_app")
if not cookies.ready():
    st.stop()

#  CHECKING SESSION STATE
if "cookies_saved" not in st.session_state:
    st.session_state.cookies_saved = False

if "user_id" not in st.session_state:
    if "user_id" in cookies:
        st.session_state.user_id = cookies["user_id"]
    else:
        st.session_state.user_id = None

if "project_id" not in st.session_state:
    st.session_state.project_id = None

if "chat_id" not in st.session_state:
    st.session_state.chat_id = None

if "user_id" in cookies and not is_valid_uuid(cookies["user_id"]):
    cookies["user_id"] = ""
    if not st.session_state.cookies_saved:
        cookies.save()
        st.session_state.cookies_saved = True
    st.session_state.user_id = None

# LOGIN/SIGNUP UI
if "signup_success" not in st.session_state:
    st.session_state.signup_success = False

if st.session_state.user_id is None:
    st.title("YELLOW Login")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        if st.session_state.signup_success:
            st.success("✅ Verification email has been sent to your email. Please verify your account before logging in.")
            st.session_state.signup_success = False
        else:
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                uid = login(email, password)
                if uid:
                    st.session_state.user_id = uid
                    cookies["user_id"] = uid
                    if not st.session_state.cookies_saved:
                        cookies.save()
                        st.session_state.cookies_saved = True
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    with tab2:
        email = st.text_input("Email", key="s_email")
        password = st.text_input("Password", type="password", key="s_pass")

        if st.button("Signup"):
            uid, err = signup(email, password)
            if uid:
                st.session_state.signup_success = True
                st.rerun()
            else:
                st.error(err or "User already exists")

    st.stop()
print("User ID in session:", st.session_state.user_id)
#  SIDEBAR: PROJECTS + CHATS 
st.sidebar.title(" Workspace")

projects = get_projects(st.session_state.user_id)

for pid, pname in projects:
    colp1, colp2 = st.sidebar.columns([8, 1])

    if colp1.button(f" {pname}", key=f"proj-{pid}"):
        st.session_state.project_id = pid
        st.session_state.chat_id = None
        st.rerun()

    if colp2.button("🗑", key=f"del-proj-{pid}"):
        supabase.table("messages").delete().in_("chat_id",
            [row["id"] for row in supabase.table("chats").select("id").eq("project_id", pid).execute().data]
        ).execute()
        supabase.table("chats").delete().eq("project_id", pid).execute()
        supabase.table("projects").delete().eq("id", pid).execute()

        if st.session_state.project_id == pid:
            st.session_state.project_id = None
            st.session_state.chat_id = None
        st.rerun()

    if st.session_state.project_id == pid:
        chat_rows = supabase.table("chats").select("id, title").eq("project_id", pid).order("id", desc=True).execute().data

        for row in chat_rows:
            cid, ctitle = row["id"], row["title"]
            c1, c2 = st.sidebar.columns([8, 1])

            if c1.button(f"    {ctitle}", key=f"chat-{pid}-{cid}"):
                st.session_state.chat_id = cid
                st.rerun()

            if c2.button("🗑", key=f"del-chat-{pid}-{cid}"):
                supabase.table("messages").delete().eq("chat_id", cid).execute()
                supabase.table("chats").delete().eq("id", cid).execute()
                if st.session_state.chat_id == cid:
                    st.session_state.chat_id = None
                st.rerun()

        if st.sidebar.button("+ New Chat", key=f"new-chat-{pid}"):
            cur = supabase.table("chats").insert({
                "user_id": st.session_state.user_id,
                "project_id": pid,
                "title": "New Chat"
            }).execute()
            st.session_state.chat_id = cur.data[0]["id"]
            st.rerun()

    st.sidebar.markdown("---")

st.sidebar.subheader("+ New Project")
new_project = st.sidebar.text_input("Project name")
if st.sidebar.button("Create Project"):
    if new_project:
        pid = create_project(st.session_state.user_id, new_project)
        st.session_state.project_id = pid
        st.session_state.chat_id = None
        st.rerun()
#LOGOUT BUTTON
if st.sidebar.button(" Logout"):


    for key in ["user_id", "project_id", "chat_id", "cookies_saved"]:
        if key in st.session_state:
            del st.session_state[key]
    cookies["user_id"] = ""

    if not st.session_state.get("cookies_saved", False):
        cookies.save()
        st.session_state.cookies_saved = True

    st.rerun()
# MAIN CHAT UI 
if st.session_state.chat_id is None:
    st.info("Select a chat from the sidebar or create a new one!")
    st.stop()

st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

messages = get_messages(st.session_state.chat_id)
for role, content in messages:
    css_class = "user" if role == "user" else "assistant"
    st.markdown(f"<div class='message {css_class}'>{content}</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Message", key="input")
    send = st.form_submit_button("Send")

if send and user_input:
    send_message(st.session_state.chat_id, user_input)
    supabase.table("chats").update({"title": user_input[:30]}).eq("id", st.session_state.chat_id).eq("title", "New Chat").execute()
    st.rerun()
