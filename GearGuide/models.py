from typing import Optional
from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.orm as so
from GearGuide import db

class User(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(256))
    picture_filename: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
class Trip(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    trip_name: so.Mapped[str] = so.mapped_column(sa.String(96), index=True)
    location_zip: so.Mapped[int] = so.mapped_column(sa.Integer, index=True)
    start_date: so.Mapped[datetime] = so.mapped_column(sa.Date, index=True)
    end_date: so.Mapped[datetime] = so.mapped_column(sa.Date, index=True)

    def __repr__(self):
        return '<Trip {}: \'{}\'>'.format(self.id, self.trip_name)