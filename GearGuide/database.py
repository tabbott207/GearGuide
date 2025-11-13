from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from datetime import date
from GearGuide.models import User, Trip, TripInvite, Friendship, PackListItem
from GearGuide import db

def add_user(
    username : str, 
    email : str, 
    password : str, 
    pfp_filename : str | None = None
) -> bool:
    """Adds a user with the provided arguments
    
    Returns false if insert into database fails due to a constraint being broken"""

    hashed_pass = generate_password_hash(password=password)

    user = User(
        username=username, 
        email=email, 
        password_hash=hashed_pass
    )

    if(pfp_filename is not None):
        user.pfp_filename = pfp_filename

    try:
        db.session.add(user)
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False
    
def get_user_by_username(
    username : str
) -> User | None:
    """Gets a user by their username 
    
    Returns None if no username matches in the database"""
    user = db.session.query(User).get({'username':username})
    return user

def get_user_profile(
    user_id : int
) -> User | None:
    """Gets a user by their ID
    
    Returns None if no ID matches in the database"""
    user = db.session.query(User).get({'id':user_id})
    return user

def add_trip(
    host_id : int,
    name : str,
    start_date : date,
    end_date : date,
    lat : float,
    long : float
) -> bool:
    """Inserts a trip with the given arguments
    
    Returns False when insertion fails due to a constraint being broken"""

    trip = Trip(
        host_id = host_id,
        name = name,
        start_date = start_date,
        end_date = end_date,
        lat = lat,
        long = long
    )

    try:
        db.session.add(trip)
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False
    
def get_trip(
    trip_id : int
) -> Trip | None:
    """Gets a trip based on the ID
    
    Returns None upon no ID matches"""
    trip = db.session.query(Trip).get({'id':trip_id})
    return trip

def get_users_trips(
    user_id : int   
) -> List[Trip]:
    """Gets a list of trips that the user is hosting
    
    List will be empty if no trips are being hosted by the user"""

    trips = db.session.query(Trip).filter(Trip.host_id == user_id).all()
    return trips

def invite_user_to_trip(
    user_id : int,
    trip_id : int
) -> bool:
    """Invites a user to a trip
    
    Returns False if insert fails, if user is hosting the trip,
    or if either the trip or user doesn't exist in the database
    """

    user = db.session.query(User).get({'id':user_id})
    trip = db.session.query(Trip).get({'id':trip_id})

    if(user is None or trip is None):
        return False

    if(user.id == trip.host_id):
        return False

    invite = TripInvite(user_id=user_id, trip_id=trip_id)

    try:
        db.session.add(invite)
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False