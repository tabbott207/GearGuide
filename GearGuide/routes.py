from flask import Blueprint, render_template
bp = Blueprint("main", __name__)

@bp.route("/home", endpoint="home")
def homePage(): return render_template("home.html")

@bp.route("/login", endpoint="login")
def loginPage(): return render_template("login.html")

@bp.route("/signup", endpoint="signup")
def signupPage(): return render_template("signup.html")

@bp.route("/create-trip", endpoint="create_trip")
def createTripPage(): return render_template("create-trip.html")

@bp.route("/trips", endpoint="trips")
def myTripsPage(): return render_template("trips.html")

@bp.route("/account", endpoint="account")
def myProfilePage(): return render_template("account.html")

@bp.route("/friends", endpoint="friends")
def myFriendsPage(): return render_template("friends.html")

@bp.route("/trips/<int:id>", endpoint="trip_detail")
def viewTripPage(id): return render_template("trip-detail.html")