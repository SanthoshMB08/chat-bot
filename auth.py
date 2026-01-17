from supabase_client import supabase
import uuid
def signup(email, password):
    # Basic validation
    if len(password) < 8:
        return None, "Password must be at least 8 characters long"

    try:
        result = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        if result.user:
            return result.user.id, None
        else:
            return None, "Signup failed"
    except Exception as e:
        # Auth errors
        return None, str(e)


def login(email, password):
    result = supabase.auth.sign_in_with_password({"email": email, "password": password})
    if result.user:
        return result.user.id
    return None
def reset_password(email):
    supabase.auth.reset_password_email(email)
def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False

