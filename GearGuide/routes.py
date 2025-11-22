from flask import Blueprint, render_template,redirect, url_for, request, flash

from . import db
from .models import User, Trip
from .auth import verify_user
from .database import (
    User,
    Trip,
    TripInvite,
    Friendship,
    send_friend_request,
    accept_friend_request,
    remove_friend,
    get_users_friends,
    invite_user_to_trip,
    add_user,
    get_user_by_username,
)
from werkzeug.security import generate_password_hash, check_password_hash   
from flask_login import login_user, logout_user, current_user, login_required
import requests
from datetime import datetime  
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
#from GearGuide.database import add_user, get_user_by_username


bp = Blueprint("main", __name__)


#______________________________________________
# Home and static pages


@bp.route("/", endpoint="index")
def index():
    return redirect(url_for("main.home"))

@bp.route("/home", endpoint="home")
def homePage(): return render_template("home.html")

@bp.route("/trips", methods=["GET", "POST"], endpoint="trips")
@login_required
def myTripsPage():
    if request.method == "POST":
        # Handle Accept / Decline for trip invites
        invite_trip_id = request.form.get("invite_trip_id", "").strip()
        invite_action = request.form.get("invite_action", "").strip().upper()

        if invite_trip_id and invite_action in {"ACCEPT", "DECLINE"}:
            try:
                trip_id = int(invite_trip_id)
            except ValueError:
                trip_id = None

            if trip_id is not None:
                invite = TripInvite.query.filter_by(
                    user_id=current_user.id,
                    trip_id=trip_id
                ).first()

                if invite:
                    if invite_action == "ACCEPT":
                        invite.accepted = True
                    elif invite_action == "DECLINE":
                        db.session.delete(invite)
                    db.session.commit()

        return redirect(url_for("main.trips"))

    # Trips I host
    host_trips = Trip.query.filter_by(host_id=current_user.id).all()

    # Trips I've accepted an invite to
    shared_trips = (
        db.session.query(Trip)
        .join(TripInvite, TripInvite.trip_id == Trip.id)
        .filter(
            TripInvite.user_id == current_user.id,
            TripInvite.accepted == True
        )
        .all()
    )

    # Combine & dedupe
    trips_dict = {t.id: t for t in host_trips + shared_trips}
    all_trips = list(trips_dict.values())

    # Pending invites *to* me (not accepted yet)
    pending_invites = (
        db.session.query(TripInvite, Trip, User)
        .join(Trip, Trip.id == TripInvite.trip_id)
        .join(User, User.id == Trip.host_id)
        .filter(
            TripInvite.user_id == current_user.id,
            TripInvite.accepted == False
        )
        .all()
    )

    return render_template(
        "trips.html",
        trips=all_trips,
        pending_invites=pending_invites,
    )

@bp.route("/account", methods=["GET", "POST"], endpoint="account")
@login_required
def accountPage():
    if request.method == "POST":
        form_type = request.form.get("form_type", "profile")

        # -------- PROFILE FORM: username + email --------
        if form_type == "profile":
            new_username = request.form.get("username", "").strip()
            new_email = request.form.get("email", "").strip().lower()

            changed = False

            # Username change
            if new_username != current_user.username:
                if not new_username:
                    flash("Username cannot be empty.", "danger")
                    return redirect(url_for("main.account"))

                if " " in new_username:
                    flash("Username cannot contain spaces.", "danger")
                    return redirect(url_for("main.account"))

                if len(new_username) > 30:
                    flash("Username must be at most 30 characters.", "danger")
                    return redirect(url_for("main.account"))

                existing_user = User.query.filter(
                    User.username == new_username,
                    User.id != current_user.id
                ).first()
                if existing_user:
                    flash("That username is already taken.", "danger")
                    return redirect(url_for("main.account"))

                current_user.username = new_username
                changed = True

            # Email change
            if new_email != current_user.email:
                if not new_email:
                    flash("Email cannot be empty.", "danger")
                    return redirect(url_for("main.account"))

                existing_email_user = User.query.filter(
                    User.email == new_email,
                    User.id != current_user.id
                ).first()
                if existing_email_user:
                    flash("That email is already in use.", "danger")
                    return redirect(url_for("main.account"))

                current_user.email = new_email
                changed = True

            if changed:
                db.session.commit()
                flash("Profile updated successfully.", "success")
            else:
                flash("No changes were made.", "info")

            return redirect(url_for("main.account"))

        # -------- PASSWORD FORM --------
        elif form_type == "password":
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")

            # Only proceed if they entered a new password
            if not new_password:
                flash("Please enter a new password.", "danger")
                return redirect(url_for("main.account"))

            if not current_password:
                flash("Enter your current password to set a new password.", "danger")
                return redirect(url_for("main.account"))

            if not check_password_hash(current_user.password_hash, current_password):
                flash("Current password is incorrect.", "danger")
                return redirect(url_for("main.account"))

            if new_password != confirm_password:
                flash("New password and confirmation do not match.", "danger")
                return redirect(url_for("main.account"))

            current_user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            flash("Password updated successfully.", "success")
            return redirect(url_for("main.account"))

        # -------- DELETE ACCOUNT FORM --------
        elif form_type == "delete":
            delete_password = request.form.get("delete_password", "")

            if not delete_password:
                flash("Enter your password to delete your account.", "danger")
                return redirect(url_for("main.account"))

            # Verify password
            if not check_password_hash(current_user.password_hash, delete_password):
                flash("Incorrect password. Account not deleted.", "danger")
                return redirect(url_for("main.account"))

            # Delete account entirely
            user_id = current_user.id
            logout_user()

            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()

            flash("Your account has been deleted.", "success")
            return redirect(url_for("main.home"))

    # GET
    return render_template("account.html")

@bp.route("/friends", methods=["GET", "POST"], endpoint="friends")
@login_required
def myFriendsPage():
    if request.method == "POST":
        # 1) Add friend by email/username
        friend_identifier = request.form.get("friend_identifier", "").strip()

        if friend_identifier:
            user = None
            if "@" in friend_identifier:
                user = User.query.filter_by(email=friend_identifier).first()
            else:
                user = User.query.filter_by(username=friend_identifier).first()

            if user is not None:
                # user1 = sender (current user), user2 = receiver (the friend)
                send_friend_request(current_user.id, user.id)

        # 2) Accept / deny pending friend request
        friend_request_id = request.form.get("friend_request_id", "").strip()
        friend_request_status = request.form.get("friend_request_status", "").strip()

        if friend_request_id and friend_request_status:
            try:
                other_user_id = int(friend_request_id)
            except ValueError:
                other_user_id = None

            if other_user_id is not None:
                status_upper = friend_request_status.upper()
                # user1 = sender (other user), user2 = receiver (current user)
                if status_upper == "ACCPET":
                    accept_friend_request(other_user_id, current_user.id)
                elif status_upper == "DENY":
                    remove_friend(other_user_id, current_user.id)

        # 3) Remove an existing friend
        friend_remove_id = request.form.get("friend_remove_id", "").strip()

        if friend_remove_id:
            try:
                other_user_id = int(friend_remove_id)
            except ValueError:
                other_user_id = None

            if other_user_id is not None:
                remove_friend(current_user.id, other_user_id)

    # Friends list (whatever your helper already does)
    friends = get_users_friends(current_user.id)

    # Pending requests: only ones SENT TO me (I'm user2_id)
    pending_requests = (
        db.session.query(User)
        .join(Friendship, Friendship.user1_id == User.id)  # user1 = sender
        .filter(Friendship.user2_id == current_user.id)    # user2 = current user
        .filter(Friendship.status == "PENDING")
        .all()
    )

    return render_template(
        "friends.html",
        friends=friends,
        pending_requests=pending_requests,
    )

@bp.route("/trips/<int:trip_id>", methods=["GET", "POST"], endpoint="trip_detail")
@login_required
def viewTripPage(trip_id):
    # 1) Fetch trip
    trip = Trip.query.filter_by(id=trip_id).first()
    if not trip:
        flash("Trip not found.", "danger")
        return redirect(url_for("main.trips"))

    # 2) Permission check: host OR accepted invitee
    is_host = (trip.host_id == current_user.id)

    if not is_host:
        invite = TripInvite.query.filter_by(
            user_id=current_user.id,
            trip_id=trip.id,
            accepted=True
        ).first()
        if invite is None:
            flash("You do not have permission to view this trip.", "danger")
            return redirect(url_for("main.trips"))

    if request.method == "POST":
        form_type = request.form.get("form_type", "").strip()

        # --- Delete trip (host only) ---
        if request.form.get("delete_trip") or form_type == "delete_trip":
            if is_host:
                # Delete related invites first
                db.session.query(TripInvite).filter(
                    TripInvite.trip_id == trip.id
                ).delete(synchronize_session=False)

                # Optionally also delete pack list items if you use that
                # from GearGuide.database import PackListItem  (already imported if needed)
                try:
                    from .database import PackListItem
                    db.session.query(PackListItem).filter(
                        PackListItem.trip_id == trip.id
                    ).delete(synchronize_session=False)
                except Exception:
                    # If PackListItem isn't imported/used, just ignore
                    pass

                db.session.delete(trip)
                db.session.commit()
                flash("Trip deleted.", "success")
            else:
                flash("Only the host can delete this trip.", "danger")
            return redirect(url_for("main.trips"))

        # --- Leave trip (secondary account) ---
        if request.form.get("leave_trip") or form_type == "leave_trip":
            if not is_host:
                invite = TripInvite.query.filter_by(
                    user_id=current_user.id,
                    trip_id=trip.id,
                    accepted=True
                ).first()
                if invite:
                    db.session.delete(invite)
                    db.session.commit()
                    flash("You have left the trip.", "success")
            else:
                flash("Host cannot leave their own trip. Delete it instead.", "danger")
            return redirect(url_for("main.trips"))

        # --- Remove another member (host only) ---
        member_remove_id = request.form.get("member_remove_id", "").strip()
        if member_remove_id:
            try:
                member_id = int(member_remove_id)
            except ValueError:
                member_id = None

            if member_id is not None and is_host and member_id != trip.host_id:
                invite = TripInvite.query.filter_by(
                    user_id=member_id,
                    trip_id=trip.id,
                    accepted=True
                ).first()
                if invite:
                    db.session.delete(invite)
                    db.session.commit()
                    flash("Member removed from trip.", "success")
            return redirect(url_for("main.trip_detail", trip_id=trip.id))

        # --- Invite user to trip (host only) ---
        user_to_invite = request.form.get("user_to_invite", "").strip()

        if user_to_invite and is_host:
            # find user by email or username
            if "@" in user_to_invite:
                user = User.query.filter_by(email=user_to_invite).first()
            else:
                user = User.query.filter_by(username=user_to_invite).first()

            if user:
                # Create or reuse invite; let /trips handle acceptance
                invite_user_to_trip(user.id, trip.id)
                flash(f"Invited {user.username} to this trip.", "success")
            else:
                flash("User not found.", "danger")

    # 3) Build members list: host + accepted invitees
    host_user = User.query.get(trip.host_id)

    accepted_members = (
        db.session.query(User)
        .join(TripInvite, TripInvite.user_id == User.id)
        .filter(
            TripInvite.trip_id == trip.id,
            TripInvite.accepted == True
        )
        .all()
    )

    # Ensure host is always first and not duplicated
    members_dict = {host_user.id: host_user}
    for m in accepted_members:
        members_dict[m.id] = m
    members = list(members_dict.values())

    activities = trip.activities.split(",") if trip.activities else []

    return render_template(
        "trip-detail.html",
        trip=trip,
        activities=activities,
        members=members,
        is_host=is_host,
    )



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
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not username or not email or not password:
        flash("Please fill out all fields.", "danger")
        return redirect(url_for("main.signup"))

    if " " in username:
        flash("Username cannot contain spaces.", "danger")
        return redirect(url_for("main.signup"))

    if len(username) > 30:
        flash("Username must be at most 30 characters.", "danger")
        return redirect(url_for("main.signup"))

    # Check if username or email is taken
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