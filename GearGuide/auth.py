# functions for handling user authentication and security
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db

def verify_user(email : str, password : str) -> bool:

    # password_hash = generate_password_hash(password=password)

    # user = db.session.query(User).get({'username':username})
    user = User.query.filter_by(email=email).first()

    #if(user is None):
    #    return False

    # if(user.password_hash == password_hash):
    #    return True

    #return False

    return bool(user and check_password_hash(user.password_hash, password))
