# auth.py
from flask import Blueprint, request, redirect, url_for, render_template, jsonify, session, current_app
from models import User, Referral, Startup
from extensions import db, login_manager, limiter
from flask_login import login_user, logout_user, login_required, current_user
import google.auth.transport.requests
import google.oauth2.id_token
from google_auth_oauthlib.flow import Flow
import os

# Allow HTTP for development (required for local Google Login)
if os.environ.get('FLASK_ENV') == 'development':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Allow scope changes from Google (prevents 'Scope has changed' errors)
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

bp = Blueprint("auth", __name__, url_prefix="/auth")


# -----------------------------------------
# LOGIN
# -----------------------------------------
@bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")  # Rate limit: 5 login attempts per minute
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
    
    # Set Sentry user context for error tracking
    try:
        from sentry_config import set_user_context
        set_user_context(user)
    except Exception as e:
        print(f"Warning: Could not set Sentry context: {e}")

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
@limiter.limit("3 per minute")  # Rate limit: 3 registration attempts per minute
def register():
    # Show signup page
    if request.method == "GET":
        return render_template("signup.html")

    data = request.form or request.json or {}

    # Enhanced validation
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    role = data.get("role", "founder")
    country = data.get("country", "").strip()
    company = data.get("company", "").strip()

    # Comprehensive field validation
    validation_errors = []
    
    if not name or len(name) < 2:
        validation_errors.append("Name must be at least 2 characters long")
    
    if not email:
        validation_errors.append("Email address is required")
    elif "@" not in email or "." not in email:
        validation_errors.append("Please enter a valid email address")
    
    if not password:
        validation_errors.append("Password is required")
    elif len(password) < 6:
        validation_errors.append("Password must be at least 6 characters long")
    
    if not company:
        validation_errors.append("Company/Organization name is required")
    
    if role not in ['startup', 'founder', 'corporate', 'enabler']:
        validation_errors.append("Please select a valid account type")

    # Role-specific validation for startups
    if role in ('startup', 'founder'):
        company_size = data.get('companySize', '').strip()
        industry = data.get('industry', '').strip()
        stage = data.get('stage', '').strip()
        
        if not company_size:
            validation_errors.append("Company size is required for startup accounts")
        if not industry:
            validation_errors.append("Industry/Sector is required for startup accounts")
        if not stage:
            validation_errors.append("Startup stage is required for startup accounts")

    if validation_errors:
        print(f"REGISTRATION: Validation failed: {validation_errors}")
        return jsonify({"error": "; ".join(validation_errors)}), 400

    # Check duplicate email
    if User.query.filter_by(email=email).first():
        print(f"REGISTRATION: Email already exists: {email}")
        return jsonify({"error": "An account with this email already exists"}), 400

    try:
        # Create new user
        print(f"REGISTRATION: Creating user {name} ({email}) with role {role}")
        user = User(
            name=name,
            email=email,
            role=role,
            country=country,
            company=company,
        )
        user.set_password(password)

        db.session.add(user)
        db.session.flush()  # Get user.id before creating startup
        print(f"REGISTRATION: Created user ID {user.id}")
        
        # Log as a Lead for the Admin Dashboard (specifically for Investor Hub/Corporate Hub users)
        if role in ('corporate', 'enabler'):
            from models import Lead
            lead_type = 'investor' if role == 'corporate' else 'enabler_app'
            new_lead = Lead(
                type=lead_type,
                name=name,
                email=email,
                company=company,
                subject=f"New {role.capitalize()} registration",
                message=f"A new {role} user registered: {name} ({company})"
            )
            db.session.add(new_lead)
            print("REGISTRATION: Added Lead record")

        # Create Startup record for startup users with additional details
        if role in ('startup', 'founder'):
            import json
            company_size = data.get('companySize', '')
            industry = data.get('industry', '')
            stage = data.get('stage', '')
            website = data.get('website', '')
            
            startup = Startup(
                founder_id=user.id,
                name=company or name,  # Use company name or user name
                website=website,
                team_size=company_size,
                stage=stage,
                sectors=json.dumps([industry] if industry else []),
                country=country or 'India'
            )
            db.session.add(startup)
            print("REGISTRATION: Added Startup record")

        db.session.commit()
        print("REGISTRATION: Database commit successful")

        # Send welcome email
        try:
            from email_service import send_welcome_email
            send_welcome_email(user)
            print("REGISTRATION: Welcome email sent")
        except Exception as e:
            print(f"REGISTRATION: Warning - Could not send welcome email: {e}")
            # Don't fail registration if email fails

        # Auto-login the user after registration
        from flask_login import login_user
        login_user(user)

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
                print("REGISTRATION: Updated referral record")
            session.pop('referral_token', None)

        # Always return JSON for POST success if it's an AJAX request (fetch)
        # Or just always for this specific endpoint POST
        return jsonify({
            "success": True, 
            "message": "Account created successfully", 
            "user": user.to_dict(), 
            "role": user.role,
            "redirect_url": f"/account-success?user_id={user.id}"
        })

    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"REGISTRATION: Error during registration: {e}")
        traceback.print_exc()
        return jsonify({"error": "An error occurred during registration. Please try again."}), 500


# -----------------------------------------
# LOGOUT
# -----------------------------------------
@bp.route("/logout")
@login_required
def logout():
    # Clear Sentry user context
    try:
        from sentry_config import clear_user_context
        clear_user_context()
    except Exception as e:
        print(f"Warning: Could not clear Sentry context: {e}")
    
    logout_user()
    return redirect("/")


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


@bp.route("/google/config-check")
def google_config_check():
    """Check if Google OAuth is properly configured"""
    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
    
    # Check if it's a real-looking key (usually ends in .apps.googleusercontent.com)
    is_real_client_id = client_id and ('.apps.googleusercontent.com' in client_id)
    
    configured = bool(client_id and client_secret and is_real_client_id)
    
    # Debug logging for Render
    print(f"GOOGLE_CONFIG_CHECK: configured={configured}")
    print(f"GOOGLE_CONFIG_CHECK: client_id_exists={bool(client_id)}")
    print(f"GOOGLE_CONFIG_CHECK: client_secret_exists={bool(client_secret)}")
    print(f"GOOGLE_CONFIG_CHECK: is_real_client_id={is_real_client_id}")
    
    return jsonify({
        "configured": configured,
        "missing_client_id": not client_id,
        "missing_client_secret": not client_secret,
        "is_placeholder": bool(client_id and not is_real_client_id),
        "redirect_uri": url_for('auth.google_callback', _external=True)
    })


@bp.route("/google/signup-data")
def google_signup_data():
    """Get stored Google signup data from session"""
    data = session.get('google_signup_data')
    if not data:
        return jsonify({"success": False, "error": "No signup data"}), 404
    return jsonify({"success": True, "data": data})
@bp.route("/google/login")
def google_login():
    """Initiate Google OAuth login flow"""
    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
    
    # Check if Google OAuth is configured with real keys
    if not client_id or '.apps.googleusercontent.com' not in client_id:
        return render_template("login.html", error="google_not_configured")
    
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": current_app.config['GOOGLE_CLIENT_ID'],
                "client_secret": current_app.config['GOOGLE_CLIENT_SECRET'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [url_for('auth.google_callback', _external=True)]
            }
        },
        scopes=['openid', 'email', 'profile']
    )
    
    # Determine redirect URI
    if os.environ.get('FLASK_ENV') == 'development':
        redirect_uri = f"http://localhost:5001{url_for('auth.google_callback')}"
    else:
        # On Render, url_for(..., _external=True) might return http due to proxy
        # Force https or use RENDER_EXTERNAL_URL
        render_url = os.environ.get('RENDER_EXTERNAL_URL')
        if render_url:
            redirect_uri = f"{render_url.rstrip('/')}{url_for('auth.google_callback')}"
        else:
            redirect_uri = url_for('auth.google_callback', _external=True, _scheme='https')
            
    flow.redirect_uri = redirect_uri
    
    # Store role and referral info in session for after OAuth
    role = request.args.get('role', 'startup')
    session['oauth_role'] = role
    session['oauth_is_login'] = role == 'login'  # Distinguish login vs signup
    
    # Store referral token if present
    ref_token = request.args.get('ref')
    if ref_token:
        session['oauth_referral_token'] = ref_token
    
    print(f"GOOGLE OAUTH: Forcing Redirect URI to {redirect_uri}", flush=True)
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    session['oauth_state'] = state
    return redirect(authorization_url)


@bp.route("/google/callback")
def google_callback():
    """Handle Google OAuth callback"""
    try:
        if not current_app.config.get('GOOGLE_CLIENT_ID'):
            return jsonify({"error": "Google OAuth not configured"}), 500
        
        # Verify state parameter
        if request.args.get('state') != session.get('oauth_state'):
            return jsonify({"error": "Invalid state parameter"}), 400
        
        # Determine redirect URI
        if os.environ.get('FLASK_ENV') == 'development':
            redirect_uri = f"http://localhost:5001{url_for('auth.google_callback')}"
        else:
            # Force https on Render
            render_url = os.environ.get('RENDER_EXTERNAL_URL')
            if render_url:
                redirect_uri = f"{render_url.rstrip('/')}{url_for('auth.google_callback')}"
            else:
                redirect_uri = url_for('auth.google_callback', _external=True, _scheme='https')

        # Create flow instance
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": current_app.config['GOOGLE_CLIENT_ID'],
                    "client_secret": current_app.config['GOOGLE_CLIENT_SECRET'],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri]
                }
            },
            scopes=['openid', 'email', 'profile']
        )
        
        flow.redirect_uri = redirect_uri
        
        print(f"DEBUG: Processing callback with Redirect URI: {redirect_uri}", flush=True)
        
        # Fetch token
        flow.fetch_token(authorization_response=request.url)
        
        # Verify the token
        credentials = flow.credentials
        request_session = google.auth.transport.requests.Request()
        
        print(f"DEBUG: Verifying Google Token for Client ID: {current_app.config['GOOGLE_CLIENT_ID']}", flush=True)
        
        id_info = google.oauth2.id_token.verify_oauth2_token(
            credentials.id_token, 
            request_session, 
            current_app.config['GOOGLE_CLIENT_ID'],
            clock_skew_in_seconds=10
        )
        
        print("DEBUG: Google Token Verified Successfully")
        
        # Extract user info
        google_id = id_info.get('sub')
        email = id_info.get('email')
        name = id_info.get('name')
        picture = id_info.get('picture')

        # Check for existing user by Google ID or email
        user = User.query.filter((User.google_id == google_id) | (User.email == email)).first()
        
        if user:
            # User exists, log them in
            if not user.is_active:
                return jsonify({"error": "Account disabled"}), 403
            
            # Update Google ID and Profile Pic if needed
            user.profile_pic = picture  # Always update/sync picture
            if not user.google_id:
                user.google_id = google_id
            db.session.commit()
            
            login_user(user)
            
            # Handle referral tracking
            token = session.get('oauth_referral_token')
            if token:
                ref = Referral.query.filter_by(token=token).first()
                if ref and user.role in ('founder', 'startup'):
                    if user.startups:
                        ref.startup_id = user.startups[0].id
                    ref.startup_name = user.name
                    ref.startup_email = user.email
                    ref.status = 'accepted'
                    db.session.commit()
                session.pop('oauth_referral_token', None)
            
            # Clean up session
            session.pop('oauth_state', None)
            session.pop('oauth_role', None)
            session.pop('oauth_is_login', None)
            
            # Redirect based on role
            if user.role == "startup":
                return redirect("/startup")
            elif user.role == "corporate":
                return redirect("/corporate")
            elif user.role == "enabler":
                return redirect("/enabler")
            elif user.role == "admin":
                return redirect("/admin")
            else:
                return redirect("/")
        
        else:
            # Check if this was a login attempt (user doesn't exist)
            is_login = session.get('oauth_is_login', False)
            if is_login:
                return redirect("/login?error=no_account")
            
            # New user - redirect to complete signup with pre-filled info
            session['google_signup_data'] = {
                'google_id': google_id,
                'email': email,
                'name': name,
                'picture': picture,
                'role': session.get('oauth_role', 'startup')
            }
            
            # Clean up OAuth session data
            session.pop('oauth_state', None)
            session.pop('oauth_is_login', None)
            
            return redirect(f"/signup?google=1&role={session.get('oauth_role', 'startup')}")
    
    except Exception as e:
        import traceback
        print(f"CRITICAL: Google OAuth error in callback: {e}")
        traceback.print_exc()
        return redirect("/signup?error=oauth_failed")


@bp.route("/google/signup/complete", methods=["POST"])
def google_signup_complete():
    """Complete Google OAuth signup with additional info"""
    google_data = session.get('google_signup_data')
    if not google_data:
        return jsonify({"error": "No Google signup data found"}), 400
    
    data = request.form or request.json or {}
    
    # Get data from form and Google
    form_name = data.get('name', '').strip()
    name = form_name or google_data.get('name', '').strip()
    email = google_data.get('email', '').strip().lower()
    google_id = google_data.get('google_id')
    role = data.get('role') or google_data.get('role', 'startup')
    company = data.get('company', '').strip()
    country = data.get('country', '').strip()
    
    # Validation
    validation_errors = []
    
    if not company:
        validation_errors.append("Company/Organization name is required")
    
    if role not in ['startup', 'founder', 'corporate', 'enabler']:
        validation_errors.append("Please select a valid account type")
    
    # Role-specific validation for startups
    if role in ('startup', 'founder'):
        company_size = data.get('companySize', '').strip()
        industry = data.get('industry', '').strip()
        stage = data.get('stage', '').strip()
        
        if not company_size:
            validation_errors.append("Company size is required for startup accounts")
        if not industry:
            validation_errors.append("Industry/Sector is required for startup accounts")
        if not stage:
            validation_errors.append("Startup stage is required for startup accounts")
    
    if validation_errors:
        return jsonify({"error": "; ".join(validation_errors)}), 400
    
    # Check if email already exists (shouldn't happen, but safety check)
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with this email already exists"}), 400
    
    try:
        # Create new user
        user = User(
            name=name,
            email=email,
            role=role,
            country=country,
            company=company,
            google_id=google_id,
            profile_pic=google_data.get('picture'),
            is_active=True
        )
        
        # Safety net: Set a dummy password in case the database still requires it
        import secrets
        user.set_password(secrets.token_urlsafe(16))
        
        db.session.add(user)
        db.session.flush()
        print(f"DEBUG: Created user ID {user.id} for {email}", flush=True)
        
        # Log as a Lead
        if role in ('corporate', 'enabler'):
            from models import Lead
            lead_type = 'investor' if role == 'corporate' else 'enabler_app'
            new_lead = Lead(
                type=lead_type,
                name=name,
                email=email,
                company=company,
                subject=f"New {role.capitalize()} registration (Google)",
                message=f"A new {role} user registered via Google: {name} ({company})"
            )
            db.session.add(new_lead)
            print("DEBUG: Added Lead record", flush=True)
        
        # Create Startup record
        if role in ('startup', 'founder'):
            import json
            company_size = data.get('companySize', '')
            industry = data.get('industry', '')
            stage = data.get('stage', '')
            website = data.get('website', '')
            
            startup = Startup(
                founder_id=user.id,
                name=company or name,
                website=website,
                team_size=company_size,
                stage=stage,
                sectors=json.dumps([industry] if industry else []),
                country=country or 'India'
            )
            db.session.add(startup)
            print("DEBUG: Added Startup record", flush=True)
        
        db.session.commit()
        print("DEBUG: Database commit successful", flush=True)
        
        # Handle referral tracking
        token = session.get('oauth_referral_token')
        if token:
            ref = Referral.query.filter_by(token=token).first()
            if ref and user.role in ('founder', 'startup'):
                if user.startups:
                    ref.startup_id = user.startups[0].id
                ref.startup_name = user.name
                ref.startup_email = user.email
                ref.status = 'accepted'
                db.session.commit()
            session.pop('oauth_referral_token', None)
        
        # Clean up session
        session.pop('google_signup_data', None)
        session.pop('oauth_role', None)
        
        # Auto-login the user
        login_user(user)
        
        return jsonify({
            "success": True,
            "message": "Account created successfully",
            "user": user.to_dict(),
            "role": user.role,
            "redirect_url": f"/account-success?user_id={user.id}"
        })
    
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"CRITICAL: Google signup completion error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# -----------------------------------------
# FORGOT PASSWORD - OTP SYSTEM
# -----------------------------------------
import random
import string
from datetime import datetime, timedelta
from email_service import send_email

@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("forgot_password.html")
    
    # POST - Send OTP
    data = request.get_json()
    email = data.get("email")
    
    if not email:
        return jsonify({"error": "Email is required"}), 400
    
    # Check if user exists
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "No account found with this email"}), 404
    
    # Generate 6-digit OTP
    otp = ''.join(random.choices(string.digits, k=6))
    
    # Store OTP in database (expires in 10 minutes)
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    try:
        # Delete any existing OTPs for this user
        db.session.execute(
            db.text("DELETE FROM password_reset_otp WHERE user_id = :user_id"),
            {"user_id": user.id}
        )
        
        # Insert new OTP
        db.session.execute(
            db.text("""
                INSERT INTO password_reset_otp (user_id, email, otp, expires_at, is_used)
                VALUES (:user_id, :email, :otp, :expires_at, 0)
            """),
            {
                "user_id": user.id,
                "email": email,
                "otp": otp,
                "expires_at": expires_at
            }
        )
        db.session.commit()
        
        # Send OTP via email
        subject = "Password Reset Code - Alchemy"
        text_body = f"""
Hi {user.name},

You requested to reset your password for your Alchemy account.

Your verification code is: {otp}

This code will expire in 10 minutes.

If you didn't request this, please ignore this email.

Best regards,
The Alchemy Team
"""
        
        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #000;">Password Reset Request</h2>
        <p>Hi <strong>{user.name}</strong>,</p>
        <p>You requested to reset your password for your Alchemy account.</p>
        <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
            <p style="margin: 0; font-size: 14px; color: #666;">Your verification code is:</p>
            <h1 style="margin: 10px 0; font-size: 36px; letter-spacing: 8px; color: #000;">{otp}</h1>
            <p style="margin: 0; font-size: 14px; color: #666;">This code will expire in 10 minutes</p>
        </div>
        <p>If you didn't request this, please ignore this email.</p>
        <p>Best regards,<br><strong>The Alchemy Team</strong></p>
    </div>
</body>
</html>
"""
        
        send_email(email, subject, text_body, html_body)
        
        return jsonify({"message": "Verification code sent to your email"}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error sending OTP: {e}")
        return jsonify({"error": "Failed to send verification code"}), 500


@bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "GET":
        return render_template("verify_otp.html")
    
    # POST - Verify OTP
    data = request.get_json()
    email = data.get("email")
    otp = data.get("otp")
    
    if not email or not otp:
        return jsonify({"error": "Email and OTP are required"}), 400
    
    try:
        # Check if OTP is valid
        result = db.session.execute(
            db.text("""
                SELECT id, user_id, expires_at, is_used 
                FROM password_reset_otp 
                WHERE email = :email AND otp = :otp
                ORDER BY created_at DESC
                LIMIT 1
            """),
            {"email": email, "otp": otp}
        ).fetchone()
        
        if not result:
            return jsonify({"error": "Invalid verification code"}), 400
        
        otp_id, user_id, expires_at, is_used = result
        
        # Check if already used
        if is_used:
            return jsonify({"error": "This code has already been used"}), 400
        
        # Check if expired
        if datetime.utcnow() > expires_at:
            return jsonify({"error": "Verification code has expired"}), 400
        
        return jsonify({"message": "Code verified successfully"}), 200
        
    except Exception as e:
        print(f"Error verifying OTP: {e}")
        return jsonify({"error": "Failed to verify code"}), 500


@bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "GET":
        return render_template("reset_password.html")
    
    # POST - Reset password
    data = request.get_json()
    email = data.get("email")
    otp = data.get("otp")
    password = data.get("password")
    
    if not email or not otp or not password:
        return jsonify({"error": "All fields are required"}), 400
    
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    
    try:
        # Verify OTP one more time
        result = db.session.execute(
            db.text("""
                SELECT id, user_id, expires_at, is_used 
                FROM password_reset_otp 
                WHERE email = :email AND otp = :otp
                ORDER BY created_at DESC
                LIMIT 1
            """),
            {"email": email, "otp": otp}
        ).fetchone()
        
        if not result:
            return jsonify({"error": "Invalid verification code"}), 400
        
        otp_id, user_id, expires_at, is_used = result
        
        if is_used:
            return jsonify({"error": "This code has already been used"}), 400
        
        if datetime.utcnow() > expires_at:
            return jsonify({"error": "Verification code has expired"}), 400
        
        # Get user and update password
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user.set_password(password)
        
        # Mark OTP as used
        db.session.execute(
            db.text("UPDATE password_reset_otp SET is_used = 1 WHERE id = :otp_id"),
            {"otp_id": otp_id}
        )
        
        db.session.commit()
        
        return jsonify({"message": "Password reset successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error resetting password: {e}")
        return jsonify({"error": "Failed to reset password"}), 500
