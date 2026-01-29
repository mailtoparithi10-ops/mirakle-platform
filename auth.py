# auth.py
from flask import Blueprint, request, redirect, url_for, render_template, jsonify, session
from models import User, Referral, Startup
from extensions import db, login_manager
from flask_login import login_user, logout_user, login_required, current_user


bp = Blueprint("auth", __name__, url_prefix="/auth")


# -----------------------------------------
# LOGIN
# -----------------------------------------
@bp.route("/login", methods=["GET", "POST"])
def login():
    # If GET request → show login page
    if request.method == "GET":
        return render_template("login.html")

    # If POST request → process login (form or JSON)
    json_data = request.get_json(silent=True)
    data = request.form or json_data or {}
    
    print(f"\n=== LOGIN ATTEMPT ===")
    print(f"Method: {request.method}")
    print(f"Form data: {dict(request.form)}")
    print(f"JSON data: {json_data}")
    print(f"Is AJAX: {request.headers.get('X-Requested-With') == 'XMLHttpRequest'}")

    email = data.get("email")
    password = data.get("password")
    
    print(f"Email: {email}")
    print(f"Password: {'*' * len(password) if password else 'None'}")

    if not email or not password:
        print("ERROR: Missing credentials")
        return jsonify({"error": "Missing credentials"}), 400

    user = User.query.filter_by(email=email).first()
    print(f"User found: {user is not None}")
    
    if user:
        print(f"User email: {user.email}, Role: {user.role}, Active: {user.is_active}")
        password_valid = user.check_password(password)
        print(f"Password valid: {password_valid}")

    if not user or not user.check_password(password):
        print("ERROR: Invalid credentials")
        return jsonify({"error": "Invalid email or password"}), 401

    if not user.is_active:
        print("ERROR: Account disabled")
        return jsonify({"error": "Account disabled"}), 403

    login_user(user)
    print(f"SUCCESS: User logged in - {user.email}")

    # --- REFERRAL TRACKING ---
    token = session.get('referral_token')
    if token:
        ref = Referral.query.filter_by(token=token).first()
        if ref and user.role in ('founder', 'startup'):
            # Link to user's first startup
            if user.startups:
                ref.startup_id = user.startups[0].id
                ref.startup_name = user.name
                ref.startup_email = user.email
                ref.status = 'accepted'
                db.session.commit()
        session.pop('referral_token', None)

    # Always return JSON for fetch/AJAX requests (which is what the frontend uses)
    # The frontend JavaScript will handle the redirect
    return jsonify({
        "success": True, 
        "message": "Login successful", 
        "user": user.to_dict(), 
        "role": user.role
    })


# -----------------------------------------
# REGISTER
# -----------------------------------------
@bp.route("/register", methods=["GET", "POST"])
def register():
    # Show register page
    if request.method == "GET":
        return render_template("register.html")

    data = request.form or request.json or {}

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "founder")
    country = data.get("country")
    company = data.get("company")

    if not name or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    # Check duplicate email
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    # Create new user
    user = User(
        name=name,
        email=email,
        role=role,
        country=country,
        company=company,
    )
    user.set_password(password)

    db.session.add(user)
    
    # NEW: Log as a Lead for the Admin Dashboard (specifically for Investor Hub/Corporate Hub users)
    if role in ('corporate', 'connector'):
        from models import Lead
        lead_type = 'investor' if role == 'corporate' else 'connector_app'
        new_lead = Lead(
            type=lead_type,
            name=name,
            email=email,
            company=company,
            subject=f"New {role.capitalize()} registration",
            message=f"A new {role} user registered: {name} ({company})"
        )
        db.session.add(new_lead)

    db.session.commit()

    login_user(user)

    # --- REFERRAL TRACKING ---
    token = session.get('referral_token')
    if token:
        ref = Referral.query.filter_by(token=token).first()
        if ref and user.role in ('founder', 'startup'):
            # Link to user's first startup if exists, or wait for one to be created
            # During registration, startups might not be created yet.
            # But normally 'founder' creates a startup in dashboard.
            # For now, just store the email and name
            ref.startup_name = user.name
            ref.startup_email = user.email
            ref.status = 'accepted'
            db.session.commit()
        session.pop('referral_token', None)

    if request.is_json:
        return jsonify({"success": True, "message": "Registration successful", "user": user.to_dict(), "role": user.role})

    # Redirect based on user role
    if user.role == "admin":
        return redirect("/admin")
    elif user.role == "startup" or user.role == "founder":
        return redirect("/startup")
    elif user.role == "corporate":
        return redirect("/corporate")
    elif user.role == "connector" or user.role == "enabler":
        return redirect("/connector")
    else:
        return redirect("/")


# -----------------------------------------
# LOGOUT
# -----------------------------------------
@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login.html")


# -----------------------------------------
# USER LOADER FOR FLASK-LOGIN
# -----------------------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@bp.route("/status")
def status():
    if current_user.is_authenticated:
        return jsonify({
            "is_authenticated": True,
            "role": current_user.role,
            "name": current_user.name
        })
    return jsonify({"is_authenticated": False})
