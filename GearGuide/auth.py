# functions for handling user authentication and security
from werkzeug.security import generate_password_hash
from GearGuide.models import User
from GearGuide import db

def verify_user(username : str, password : str) -> bool:

    password_hash = generate_password_hash(password=password)

    user = db.session.query(User).get({'username':username})

    if(user is None):
        return False

    if(user.password_hash == password_hash):
        return True

    return False
