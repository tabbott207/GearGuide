from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from datetime import date
from GearGuide.models import User, Trip, TripInvite, Friendship, PackListItem
from GearGuide import db
from typing import List
from sqlalchemy import or_

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
    # user = db.session.query(User).get({'username':username})
    return User.query.filter_by(username=username).first()

def get_user_profile(
    user_id : int
) -> User | None:
    """Gets a user by their ID
    
    Returns None if no ID matches in the database"""
    # user = db.session.query(User).get({'id':user_id})
    return User.query.get(user_id)

def add_trip(
    host_id : int,
    name : str,
    destination : str,
    start_date : date,
    end_date : date,
    lat : float,
    lon : float,
    activities : list[str] | None = None,
    notes : str | None = None
) -> bool:
    """Inserts a trip with the given arguments
    
    Returns False when insertion fails due to a constraint being broken"""

    trip = Trip(
        host_id = host_id,
        name = name,
        start_date = start_date,
        end_date = end_date,
        lat = lat,
        lon = lon,
        activities = ",".join(activities) if activities else "",
        notes = notes or ""
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
    # trip = db.session.query(Trip).get({'id':trip_id})
    return Trip.query.get(trip_id)

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
    user1_id: int,  # sender
    user2_id: int   # receiver
) -> bool:
    """Create a pending friend request from user1_id to user2_id.

    Uses user1_id/user2_id as a sorted pair in the table, and stores
    initiator_id as the actual sender. If an old row exists without
    initiator_id, we update it.
    """

    if user1_id == user2_id:
        return False

    sender_id = user1_id
    receiver_id = user2_id

    # normalize pair to satisfy check_user1_lt_user2
    low = min(sender_id, receiver_id)
    high = max(sender_id, receiver_id)

    existing = (
        db.session.query(Friendship)
        .filter_by(user1_id=low, user2_id=high)
        .first()
    )

    if existing:
        # If there's an old row with NULL initiator_id, patch it
        if existing.status == "PENDING" and existing.initiator_id is None:
            existing.initiator_id = sender_id
            db.session.commit()
            return True

        # If it is already pending or accepted with initiator set, treat as success
        if existing.status in ("PENDING", "ACCEPTED"):
            return True

        # If blocked, do nothing
        if existing.status == "BLOCKED":
            return False

    friendship = Friendship(
        user1_id=low,
        user2_id=high,
        status="PENDING",
        initiator_id=sender_id
    )

    try:
        db.session.add(friendship)
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False

def accept_friend_request(user1_id: int, user2_id: int) -> None:
    """
    Accept a friend request between user1_id and user2_id,
    regardless of who sent it (we normalize the pair).
    """
    low = min(user1_id, user2_id)
    high = max(user1_id, user2_id)

    friendship = (
        db.session.query(Friendship)
        .filter_by(user1_id=low, user2_id=high)
        .first()
    )

    if friendship is None:
        return

    friendship.status = "ACCEPTED"
    db.session.commit()


def remove_friend(user1_id: int, user2_id: int) -> None:
    """
    Remove a friendship or pending request between user1_id and user2_id,
    regardless of who originally sent it.
    """
    low = min(user1_id, user2_id)
    high = max(user1_id, user2_id)

    friendship = (
        db.session.query(Friendship)
        .filter_by(user1_id=low, user2_id=high)
        .first()
    )

    if friendship is None:
        return

    db.session.delete(friendship)
    db.session.commit()

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

def get_pack_list(
    trip_id : int
) -> List[PackListItem]:
    """Gets the pack list items associated with a trip
    
    Can return an empty list if none exist"""

    items = (
        db.session.query(PackListItem)
        .filter(PackListItem.trip_id == trip_id)
        .all()
    )

    return items

def update_pack_item_status(
    item_id : int,
    is_packed : bool
) -> bool:
    """Updates an items status on the pack list
    
    Returns the success of the operation"""

    item = db.session.query(PackListItem).get({'id':item_id})

    if(item is None):
        return False

    item.is_packed = is_packed

    db.session.commit()
    return True

def remove_pack_item(
    item_id : int
) -> bool:
    """removes an item from the pack list
        
    Returns the success of the operation"""

    item = db.session.query(PackListItem).get({'id':item_id})

    if(item is None):
        return False

    db.session.delete(item)
    db.session.commit()
    return True