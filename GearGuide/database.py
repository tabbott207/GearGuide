from werkzeug.security import generate_password_hash
from GearGuide.models import User, Trip, TripInvite, Friendship, PackListItem
from GearGuide import db

def add_user(
    username : str, 
    email : str, 
    password : str, 
    pfp_filename : str | None = None
) -> bool:

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
