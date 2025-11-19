from flask import Blueprint, render_template,redirect, url_for, request, flash

from . import db
from .models import User, Trip
from .auth import verify_user
from werkzeug.security import generate_password_hash, check_password_hash   
from flask_login import login_user, logout_user, current_user, login_required
import requests
from datetime import datetime  
from sqlalchemy.exc import IntegrityError
# from sqlalchemy import or_
#from GearGuide.database import add_user, get_user_by_username


bp = Blueprint("main", __name__)


#______________________________________________
# Home and static pages


@bp.route("/", endpoint="index")
def index():
    return redirect(url_for("main.home"))

@bp.route("/home", endpoint="home")
def homePage(): return render_template("home.html")

@bp.route("/trips", endpoint="trips")
@login_required
def myTripsPage(): 
    user_trips = Trip.query.filter_by(host_id=current_user.id).all()
    return render_template("trips.html", trips = user_trips)

@bp.route("/account", endpoint="account")
def myProfilePage(): return render_template("account.html")

@bp.route("/friends", endpoint="friends")
def myFriendsPage(): return render_template("friends.html")

@bp.route("/trips/<int:trip_id>", endpoint="trip_detail")
@login_required
def viewTripPage(trip_id): 
    trip = Trip.query.filter_by(id=trip_id, host_id=current_user.id).first()
    if not trip:
        flash("Trip not found, or you do not have permission to view it.", "danger")
        return redirect(url_for("main.trips"))
    
    activities = trip.activities.split(",") if trip.activities else []
    
    return render_template("trip-detail.html", trip = trip, activities = activities)



#______________________________________________
# Login routes (GET + POST)


@bp.route("/login", methods=["GET"], endpoint="login")
def loginPage(): return render_template("login.html")

@bp.route("/login", methods=["POST"])
def loginSubmit():
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        flash("Please fill out all fields.", "danger")
        return redirect(url_for("main.login"))

    if not verify_user(email, password):
        flash("Invalid email or password. Please try again.", "danger")
        return redirect(url_for("main.login"))
    

    #if not user or not check_password_hash(user.password_hash, password):
    #    flash("Invalid email or password.", "danger")
    #    return redirect(url_for("main.login"))
    
    user = User.query.filter_by(email=email).first()
    login_user(user)
    flash(f"Login successful! Welcome, {user.username}!", "success")
    return redirect(url_for("main.home"))


    # flash("Login POST received (not implemented yet).", "info")
    # return redirect(url_for("main.login"))



#______________________________________________
# Signup routes (GET + POST)


@bp.route("/signup", methods=["GET"], endpoint="signup")
def signupPage(): return render_template("signup.html")

@bp.route("/signup", methods=["POST"])
def signupSubmit():
    username = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")

    if not username or not email or not password:
        flash("Please fill out all fields.", "danger")
        return redirect(url_for("main.signup"))
    
    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing_user:
        flash("Username or email already exists.", "danger")
        return redirect(url_for("main.signup"))
    
    hashed_password = generate_password_hash(password)
    user = User(username=username, email=email, password_hash=hashed_password)

    db.session.add(user)
    db.session.commit()
    flash("Signup successful! Please log in.", "success")
    return redirect(url_for("main.login"))


    # flash("Signup POST received (not implemented yet).", "info")
    # return redirect(url_for("main.signup"))



#______________________________________________
# Logout route 

@bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.home"))



#______________________________________________
# Create trip (GET + POST)

@bp.route("/create-trip", methods=["GET"], endpoint="create_trip")
@login_required
def createTripPage(): return render_template("create-trip.html")

@bp.route("/create-trip", methods=["POST"])
@login_required
def createTripSubmit():
    name = request.form.get("name")
    destination = request.form.get("destination")
    start_date_str = request.form.get("start_date")
    end_date_str = request.form.get("end_date")
    activities = request.form.getlist("activities")
    notes = request.form.get("notes")

    if not name or not destination or not start_date_str or not end_date_str:
        flash("Please fill out all required fields.", "danger")
        return redirect(url_for("main.create_trip"))
    
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        flash("Invalid date format.", "danger")
        return redirect(url_for("main.create_trip"))

    try:                                        #    search?format=json&limit=1&q={destination}")
        nominatum_url = f"https://nominatim.openstreetmap.org/search?q={destination}&limit=1&format=json"
        res = requests.get(nominatum_url, headers={"User-Agent": "GearGuideApp"})
        data = res.json()

        if isinstance(data, list) and len(data) > 0:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
        else:
            lat = None
            lon = None
            flash("Could not geocode the destination.", "warning")
        
    except Exception as e:
        lat = None
        lon = None
        flash("Error occurred during geocoding. {e}", "warning")

    
    trip = Trip(
        host_id = current_user.id,
        name = name,
        destination = destination,
        lat = lat,
        lon = lon,
        start_date = start_date,
        end_date = end_date,
        activities = ",".join(activities),
        notes = notes

    )

    try:
        db.session.add(trip)
        db.session.commit()

        flash("Trip created successfully!", "success")
        return redirect(url_for("main.trips"))
    except Exception as e:
        db.session.rollback()
        flash(f"Database Error: {e}", "danger")
        return redirect(url_for("main.create_trip"))



"""
    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        flash("Invalid date format.", "danger")
        return redirect(url_for("main.create_trip"))
"""

    # flash("Trip POST received (not implemented yet).", "info")
    # return redirect(url_for("main.create_trip"))



#______________________________________________
# Nominatim geocoding destination

    #lat, lon = 0.0, 0.0 # default coords are 0.0, if geocoding fails
"""
    try:
        nominatim_url = "https://nominatim.openstreetmap.org/search"
        params = {"q": destination, "format": "json", "limit": 1}
        
        res = requests.get(nominatim_url, params=params, timeout=5, headers={"User-Agent": "GearGuideApp"})
        res.raise_for_status()
        data = res.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
    except Exception:
        pass # silently fail geocoding. leaves both lat and lon as 0.0


    trip = Trip(
        host_id=current_user.id,
        name=trip_name,
        start_date=start_date,
        end_date=end_date,
        lat=lat,
        long=lon,
        #notes=notes,
        #activities=",".join(activities)
    )

    try:
        db.session.add(trip)
        db.session.commit()
        flash("Trip created successfully!", "success")
        return redirect(url_for("main.trips"))
    except Exception as e:
        db.session.rollback()
        flash("Error creating trip: {e}", "danger")
        return redirect(url_for("main.create_trip"))
"""