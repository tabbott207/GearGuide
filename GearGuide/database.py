# functions for interacting with the database
import sqlite3
from datetime import datetime

from flask import current_app

from models import Trip

TOTAL_TABLES = 6

def startDB():
    con = sqlite3.connect('GearGuide/data.sqlite3')
    cur = con.cursor()
    
    if len(cur.execute('SELECT name FROM sqlite_master').fetchall()) != TOTAL_TABLES:
        print('[database.py]: \'data.sqlite3\' is either missing or corrupted.')
        print('[database.py]: initializing new \'data.sqlite3\'.')
        initializeDB(cur, con)

def initializeDB(cur: sqlite3.Cursor, con: sqlite3.Connection):

    # Drop tables if they already exists
    cur.execute('DROP TABLE IF EXISTS user')
    cur.execute('DROP TABLE IF EXISTS trip')
    cur.execute('DROP TABLE IF EXISTS friend_request')
    cur.execute('DROP TABLE IF EXISTS friend_pairing')
    cur.execute('DROP TABLE IF EXISTS trip_whitelist')
    cur.execute('DROP TABLE IF EXISTS pack_list_item')

    # Create tables
    cur.execute('CREATE TABLE user(userID INT, username VARCHAR(31), email VARCHAR(255), passwordHash, profilePicFilename VARCHAR(128))')
    cur.execute('CREATE TABLE trip(tripID INT, userID INT, name VARCHAR(95), locationZip INT, startDate DATE, endDate DATE)')
    cur.execute('CREATE TABLE friend_request(user1ID INT, user2ID INT)')
    cur.execute('CREATE TABLE friend_pairing(user1ID INT, user2ID INT)')
    cur.execute('CREATE TABLE trip_whitelist(userID INT, tripID INT)')
    cur.execute('CREATE TABLE pack_list_item(tripID INT, itemName VARCHAR(63), is_packed BOOLEAN)')


