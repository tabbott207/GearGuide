from sqlalchemy import Column, Integer, ForeignKey, String, Date, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from GearGuide import db

class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(30), nullable=False, unique=True)
    email = Column(String(150), nullable=False, unique=True)
    password_hash = Column(String(256), nullable=False)
    pfp_filename = Column(String(250), default='profile_default.png')

    hosted_trips = relationship('Trip', back_populates='host')
    joined_trips = relationship('TripInvite', back_populates='user', cascade='all, delete-orphan')

class Trip(db.Model):
    __tablename__ = 'trips'

    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    __table_args__ = (
        CheckConstraint('end_date > start_date', name='check_start_before_end_date'),
        UniqueConstraint('host_id', 'name', name='unique_trip_name_for_host')
    )

    host = relationship('User', back_populates='hosted_trips')
    invited_users = relationship('TripInvite', back_populates='trip', cascade='all, delete-orphan')

class TripInvite(db.Model):
    __tablename__ = "trip_invites"

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    trip_id = Column(Integer, ForeignKey('trips.id', ondelete='CASCADE'), primary_key=True)

    user = relationship('User', back_populates='invited_users')
    trip = relationship('Trip', back_populates='joined_trips')