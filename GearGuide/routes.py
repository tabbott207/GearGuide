# functions for handling routing the user to it's requested webpage
from GearGuide import app
from flask import render_template

@app.route('/')
def index():
    return "index page"

@app.route('/home')
def homePage():
    return render_template('homepage.html')

@app.route('/login')
def loginPage():
    return render_template('login.html')

@app.route('/signup')
def signupPage():
    return render_template('signup.html')

@app.route('/create-trip')
def createTripPage():
    return render_template('create-trip.html')

@app.route('/trips')
def myTripsPage():
    return render_template('my-trips.html')

@app.route('/profile')
def myProfilePage():
    return render_template('my-profile.html')

@app.route('/friends')
def myFriendsPage():
    return render_template('my-friends.html')

@app.route('/trips/<int:id>')
def viewTripPage(id):
    return render_template('view-trip.html')