from typing import Optional
from datetime import date
from sqlalchemy.exc import IntegrityError
from GearGuide.models import *
from GearGuide.auth import hash_password
from GearGuide import db

def get_user(id : int) -> User | None:
    """Get a user based on there id"""
    return User.query.get({'id':id})

def add_user(
        username : str,
        password : str,
        email : str,
        pfp_filename: Optional[str] = None
) -> bool:
    """Adds a given user to the database
    
    Returns if the operation was successful"""

    user = User(username=username, password=hash_password(password), email=email)

    if(pfp_filename is str):
        user.pfp_filename = pfp_filename

    try:
        db.session.add(user)
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False

def delete_user(user : User) -> bool:
    """Deletes a given user from the database
    
    Returns if the operation was successful"""
    try:
        db.session.delete(user)
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False

def update_user(
        id : int, 
        username : str | None,
        email : str | None,
        password : str | None, 
        pfp_filename : str | None
) -> bool:
    """Updates the properties of the given user's id
    
    Returns if the operation was successful"""

    user = User.query.get({'id':id})

    if(user is None):
        return False

    if(username is str):
        user.username = username

    if(email is str):
        user.email = email

    if(password is str):
        user.password_hash = hash_password(password)

    if(pfp_filename is str):
        user.pfp_filename = pfp_filename

    try:
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False


def add_trip(trip : Trip) -> bool:
    try:
        db.session.add(trip)
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False

def get_trip(id : int) -> Trip | None:
    return Trip.query.get({'id':id})

def delete_trip(trip : Trip) -> bool:
    try:
        db.session.delete(trip)
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False

def update_trip(
    id : int,
    name : str | None,
    start_date : date | None,
    end_date : date | None
) -> bool:
    
    trip = Trip.query.get({'id':id})

    if(trip is None):
        return False
    
    if(name is str):
        trip.name = name

    if(start_date is date):
        trip.start_date = start_date

    if(end_date is date):
        trip.end_date = end_date

    try:
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False
    
def invite_user(
    trip_id : int,
    user_id : int
) -> bool:

    trip = Trip.query.get({'id':trip_id})
    user = User.query.get({'id':user_id})

    if(trip is None or user is None):
        return False
    
    if(trip.host.id == user.id):
        return False

    trip_invite = TripInvite(trip=trip, user=user)

    try:
        db.session.add(trip_invite)
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False