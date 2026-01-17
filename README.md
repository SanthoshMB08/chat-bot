Chatbot Platform (Intern Assignment)
 Overview
This project is a minimal Chatbot Platform built as part of the Software Engineer Intern assignment. It supports multi‑user authentication, project/agent creation, prompt storage, and a chat interface powered by LLM APIs.
Key features:
-  Authentication with Supabase (email/password + email verification)
-  User accounts with secure login
-  Projects/Agents creation under each user
-  Chat interface with RAG (Retrieval‑Augmented Generation) for continuity
-  LLM integration using Groq API (can be extended to OpenAI/OpenRouter)
-  Prompt storage per project
-  Supabase database for persistence
- UI templates built with Streamlit, styled using Copilot + ChatGPT CSS suggestions
-  Extensible design for future analytics and integrations

 Architecture & Design
Components
- Frontend/UI: Streamlit (templates + custom CSS)
- Backend/Auth: Supabase (Auth + Database)
- LLM Service: Groq API (Responses), extensible to OpenAI/OpenRouter
- Chat Continuity: RAG pipeline using old project resources
- Deployment: Streamlit Community Cloud (GitHub integration)
Flow
- User signs up → receives email verification link.
- After verification, user can log in with email/password.
- User creates a Project/Agent.
- Prompts are stored and associated with the project.
- Chat interface retrieves context via RAG and queries Groq API for responses.
- Responses are displayed in the Streamlit UI.

 Setup Instructions
1. Clone the repo
git clone https://github.com/<your-username>/chat-bot.git
cd chat-bot


2. Install dependencies
Make sure you have Python 3.9+.
pip install -r requirements.txt


3. Configure secrets
Create a .streamlit/secrets.toml file locally:
[supabase]
url = "https://<your-project>.supabase.co"
anon_key = "<your-supabase-anon-key>"

[groq]
api_key = "<your-groq-api-key>"


 Do not commit this file. Add it to .gitignore.
On Streamlit Cloud, paste the same TOML content into App → Settings → Secrets.
4. Run locally
streamlit run app.py


5. Deploy
- Push your repo to GitHub (without secrets).
- Go to Streamlit Community Cloud.
- Create a new app → select your repo, branch, and entrypoint (app.py).
- Add secrets in Settings → Secrets.
- Your app will be live at https://<your-app>.streamlit.app.
live demo https://yellow-ai.streamlit.app/
📂 Project Structure
chat-bot/
│── app.py              # Main Streamlit app
│── auth.py             # Signup/Login logic with Supabase
│── supabase_client.py  # Supabase client setup
│── project.py          # Project/Agent creation
|-- prompt.py           # for prompt storage and retrevel
│── chat.py             # Chat interface
│── rag.py              # RAG pipeline for context
│── requirements.txt    # Dependencies
│── README.md           # Documentation
└── .streamlit/
    └── secrets.toml    # Local secrets (ignored in Git)



