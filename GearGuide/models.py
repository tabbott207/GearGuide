from datetime import datetime

class Trip():

    __trip_id = 101

    def __init__(self, name: str, locationZipCode: int, startDate: datetime, endDate: datetime, userID: int):
        self.tripID = Trip.__trip_id
        self.userID = userID
        self.name = name
        self.locationZipCode = locationZipCode
        self.startDate = startDate
        self.endDate = endDate
        Trip.__trip_id += 1

class User():

    __user_id = 701

    def __init__(self, username: str, email: str, password_hash: str, profile_pic_filename: str):
        self.userID = User.__user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.profile_pic_filename = profile_pic_filename
        User.__user_id += 1