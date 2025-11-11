# holds functions related to security
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password : str) -> str:
    """Wrapper function for password hashing"""
    return generate_password_hash(password=password)


