from supabase import create_client
import os

# Get your Supabase URL and API key from the Supabase dashboard
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://YOUR_PROJECT.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "YOUR_ANON_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)