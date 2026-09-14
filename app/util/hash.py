import bcrypt as b

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return b.hashpw(password.encode("utf-8"), b.gensalt()).decode("utf-8")

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against a hashed password."""
    return b.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))