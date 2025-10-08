from datetime import datetime

class Trip():
    def __init__(self, name: str, locationZipCode: int, startDate: datetime, endDate: datetime):
        name = name
        locationZipCode = locationZipCode
        startDate = startDate
        endDate = endDate

class User():
    def __init__(self, username: str, email: str, password_hash: int, profile_pic_filename):
        username = username
        email = email
        password_hash = password_hash
        profile_pic_filename = profile_pic_filename