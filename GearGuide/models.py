from sqlalchemy import Column, Integer, ForeignKey, String, Date, CheckConstraint, UniqueConstraint, event, Boolean, Float
from sqlalchemy.orm import relationship
from GearGuide import db

class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(30), nullable=False, unique=True)
    email = Column(String(150), nullable=False, unique=True)
    password_hash = Column(String(256), nullable=False)
    pfp_filename = Column(String(250), default='profile_default.png')

class Trip(db.Model):
    __tablename__ = 'trips'

    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    lat = Column(Float, nullable=False)
    long = Column(Float, nullable=False)

    __table_args__ = (
        CheckConstraint('end_date > start_date', name='check_start_before_end_date'),
        CheckConstraint('start_date >= CURRENT_DATE', name='check_start_after_current_date'),
        CheckConstraint('end_date >= CURRENT_DATE', name='check_end_after_current_date'),
        UniqueConstraint('host_id', 'name', name='unique_trip_name_for_host')
    )


class TripInvite(db.Model):
    __tablename__ = "trip_invites"

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    trip_id = Column(Integer, ForeignKey('trips.id', ondelete='CASCADE'), primary_key=True)


class Friendship(db.Model):
    __tablename__ = 'friendships'

    id = Column(Integer, primary_key=True)
    user1_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user2_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    status = Column(String(20), nullable=False) # PENDING | ACCEPTED | BLOCKED

    __table_args__ = (
        UniqueConstraint('user1_id', 'user2_id', name='unique_friendship_pairings'),
        CheckConstraint('user1_id < user2_id', name='check_id1_is_lt_id2'),
        CheckConstraint('user1_id != user2_id', name='check_user_ids_not_equal')
    )

class PackListItem(db.Model):
    __tablename__ = 'pack_list_items'

    id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, ForeignKey('trips.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100), nullable=False)
    is_packed = Column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint('trip_id', 'name', name='unique_item_name_per_trip'),
    )

@event.listens_for(Friendship, 'before_insert')
def normalize_user_ids_for_friendships(mapper, connect, target):
    if target.user1_id > target.user2_id:
        target.user1_id, target.user2_id = target.user2_id, target.user1_id