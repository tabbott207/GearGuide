from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint, func, event
from sqlalchemy.orm import relationship
from GearGuide import db

class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)

    # These relationships help navigation
    friendships = relationship(
        'Friendship',
        primaryjoin="or_(User.id==Friendship.user1_id, User.id==Friendship.user2_id)",
        viewonly=True
    )

    friends = relationship(
        'Friends',
        
    )


class Trip(db.Model):
    __tablename__ = 'trips'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    trip_name = Column(String(120), nullable=False)

class Friendship(db.Model):
    __tablename__ = 'friendships'

    user1_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user2_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    status = Column(String(20), nullable=False, default='pending')  # pending | accepted | blocked

    __table_args__ = (
        UniqueConstraint('user1_id', 'user2_id', name='uq_friendship_pair'),
    )

class TripWhitelist(db.Model):
    __tablename__ = 'trip_whitelist'

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    trip_id = Column(Integer, ForeignKey('trips.id', ondelete='CASCADE'), nullable=False)

    __table_args__ = (
        UniqueConstraint('user_id', 'trip_id', name='uq_tripwhitelist')
    )

# Normalize IDs before insert — enforce (lower_id, higher_id)
@event.listens_for(Friendship, 'before_insert')
def normalize_friendship(mapper, connection, target):
    if target.user1_id > target.user2_id:
        target.user1_id, target.user2_id = target.user2_id, target.user1_id

