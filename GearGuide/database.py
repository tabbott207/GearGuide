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

    user = get_user_profile(user_id)
    trip = get_trip(trip_id)

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

def get_users_invited(
    trip_id : int
) -> List[User]:
    """Returns the users who are invited to a trip.
    
    Does not return the host and can return an empty list if none are invited"""

    users = (
        db.session.query(User)
        .join(TripInvite, User.id == TripInvite.user_id)
        .filter(TripInvite.trip_id == trip_id)
        .all()
    )

    return users 

def get_trips_invited(
    user_id : int
) -> List[Trip]:
    """Returns the trips a user is invited to.
    
    Does not return hosted trips and can return an empty list 
    if they are not invited to any"""

    trips = (
        db.session.query(Trip)
        .join(TripInvite, Trip.id == TripInvite.trip_id)
        .filter(TripInvite.user_id == user_id)
        .all()
    )

    return trips

def get_users_friends(
    user_id : int
) -> List[User]:
    """Returns the friends of a given user
    
    Can return an empty list if the user has no friends"""

    friends = (
        db.session.query(User)
        .join(Friendship, or_(Friendship.user1_id == User.id, Friendship.user2_id == User.id))
        .filter(or_(Friendship.user1_id == user_id, Friendship.user2_id == user_id))
        .filter(User.id != user_id)
        .filter(Friendship.status == 'ACCEPTED')
        .all()
    )

    return friends

def send_friend_request(
    user1_id : int,
    user2_id : int
) -> bool:
    """Adds a friend request to the database
    
    Returns false if insert fails or users don't exist"""

    user1 = get_user_profile(user1_id)
    user2 = get_user_profile(user2_id)

    if(user1 is None or user2 is None):
        return False

    request = Friendship(user1_id=user1_id, user2_id=user2_id, status='PENDING')

    try:
        db.session.add(request)
        sb.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False

def accept_friend_request(
    user1_id : int,
    user2_id : int
) -> bool:
    """Accepts a pending friend request between two users
    
    Returns success of operation"""

    if(user1_id == user2_id):
        return False

    if(user1_id > user2_id):
        user1_id, user2_id = user2_id, user1_id

    request = db.session.query(Friendship).get({'user1_id':user1_id, 'user2_id':user2_id})

    if(request is None):
        return False

    request.status = 'ACCEPTED'
    db.session.commit()
    return True

def block_user(
    user1_id : int,
    user2_id : int
) -> bool:
    """Blocks a users from each other
    
    Returns success of operation"""

    if(user1_id == user2_id):
        return False

    if(user2_id > user1_id):
        user1_id, user2_id = user2_id, user1_id

    request = db.session.query(Friendship).get({'user1_id':user1_id, 'user2_id':user2_id})

    if(request is None): # there is no friendship in the db

        request = Friendship(user1_id=user1_id, user2_id=user2_id, status='BLOCKED')

        try:
            db.session.add(request)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    else: # there is a friendship in the db
        request.status = 'BLOCKED'
        db.session.commit()
        return True

def remove_friend(
    user1_id : int,
    user2_id : int
) -> bool:
    """Removed a friendship
    
    Returns the success of the operation"""

    if(user1_id == user2_id):
        return False

    if(user2_id > user1_id):
        user1_id, user2_id = user2_id, user1_id

    request = db.session.query(Friendship).get({'user1_id':user1_id, 'user2_id':user2_id})

    if(request is None):
        return False

    db.session.delete(request)
    db.session.commit()
    return True

def add_pack_item(
    trip_id : int,
    name : str
) -> bool:
    """Adds a pack item to a trip
    
    Returns the success of the operation"""

    item = PackListItem(trip_id=trip_id, name=name)

    try:
        db.session.add(item)
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False