from werkzeug.security import generate_password_hash
from GearGuide.models import User, Trip, TripInvite, Friendship, PackListItem
from GearGuide import db

def add_user(
    username : str, 
    email : str, 
    password : str, 
    pfp_filename : str | None = None
) -> bool:
    """Adds a user with the provided arguments
    
    Returns false if insert into database fails, otherwise returns true"""

    hashed_pass = generate_password_hash(password=password)

    user = User(username=username, email=email, password_hash=hashed_pass)

    if(pfp_filename is not None):
        user.pfp_filename = pfp_filename

    try:
        db.session.add(user)
        db.session.commit()
        return True
    except ValueError:
        db.session.rollback()
        return False
    
def get_user_by_username(
    username : str
) -> User | None:
    """Gets a user by their username 
    
    If the user does not exist in the database, it returns None"""
    user = db.session.query(User).get({'username':username})
    return user