# functions for handling routing the user to it's requested webpage

from flask import Flask, render_template, current_app

@current_app.route('/home')
def homePage():
    return render_template('homepage.html')

@current_app.route('/login')
def loginPage():
    return render_template('login.html')

@current_app.route('/signup')
def signupPage():
    return render_template('signup.html')

@current_app.route('/create-trip')
def createTripPage():
    return render_template('create-trip.html')

@current_app.route('/trips')
def myTripsPage():
    return render_template('my-trips.html')

@current_app.route('/profile')
def myProfilePage():
    return render_template('my-profile.html')

@current_app.route('/friends')
def myFriendsPage():
    return render_template('my-friends.html')

@current_app.route('/trips/<int:id>')
def viewTripPage(id):
    return render_template('view-trip.html')