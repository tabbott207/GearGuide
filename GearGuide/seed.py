# app/seed.py
from GearGuide import db
from GearGuide.security import hash_password
from GearGuide.models import User, Trip, TripInvite, Friendship, PackListItem
from datetime import date, timedelta

def seed_data():
    """Seed the database with initial testing data."""

    # Clear existing data
    db.session.query(TripInvite).delete()
    db.session.query(Trip).delete()
    db.session.query(User).delete()
    db.session.query(Friendship).delete()
    db.session.query(PackListItem).delete()
    db.session.commit()

    # Create test users
    user1 = User(
        username="alice", 
        email="alice@example.com", 
        password_hash=hash_password('password12')
    )
    user2 = User(
        username="bob", 
        email="bob@example.com", 
        password_hash=hash_password('birdistheword')
    )
    user3 = User(
        username="charlie", 
        email="charlie@example.com", 
        password_hash=hash_password('admin123')
    )

    db.session.add_all([user1, user2, user3])
    db.session.commit()

    # Create trips
    trip1 = Trip(
        name="Beach Vacation",
        start_date=date.today() + timedelta(days=5),
        end_date=date.today() + timedelta(days=10),
        host_id=user1.id
    )

    trip2 = Trip(
        name="Mountain Adventure",
        start_date=date.today() + timedelta(days=15),
        end_date=date.today() + timedelta(days=20),
        host_id=user2.id
    )

    db.session.add_all([trip1, trip2])
    db.session.commit()

    # Create invitations
    invite1 = TripInvite(user_id=user2.id, trip_id=trip1.id)
    invite2 = TripInvite(user_id=user3.id, trip_id=trip1.id)
    invite3 = TripInvite(user_id=user1.id, trip_id=trip2.id)

    db.session.add_all([invite1, invite2, invite3])
    db.session.commit()

    # Create friendships
    friendship1 = Friendship(user1_id=user1.id, user2_id=user2.id, status='ACCEPTED')
    friendship2 = Friendship(user1_id=user1.id, user2_id=user3.id, status='ACCEPTED')
    friendship3 = Friendship(user1_id=user2.id, user2_id=user3.id, status='PENDING')

    db.session.add_all([friendship1, friendship2, friendship3])
    db.session.commit()

    # Create pack list items
    item1 = PackListItem(trip_id=trip1.id, name='Bathing Suit')
    item2 = PackListItem(trip_id=trip1.id, name='Sunscreen')
    item3 = PackListItem(trip_id=trip2.id, name='Sweatshirt')
    item4 = PackListItem(trip_id=trip2.id, name='Firewood')

    db.session.add_all([item1, item2, item3, item4])
    db.session.commit()

    print('done!')
