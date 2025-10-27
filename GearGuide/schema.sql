DROP TABLE IF EXISTS user
DROP TABLE IF EXISTS trip
DROP TABLE IF EXISTS friend_request
DROP TABLE IF EXISTS friendships
DROP TABLE IF EXISTS trip_whitelist
DROP TABLE IF EXISTS pack_list_item

CREATE TABLE user(userID INT, username VARCHAR(32), email TEXT, passwordHash TEXT, profilePicFilename TEXT)
CREATE TABLE trip(tripID INT, userID INT, name VARCHAR(96), locationZip INT, startDate DATE, endDate DATE)
CREATE TABLE friend_request(user1ID INT, user2ID INT, status TEXT)
CREATE TABLE friendships(user1ID INT, user2ID INT)
CREATE TABLE trip_whitelist(userID INT, tripID INT)
CREATE TABLE pack_list_item(idID INT, tripID INT, itemName TEXT, is_checked BOOLEAN)

