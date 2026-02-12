# app.py (NEW CLEAN BACKEND)
import os
from datetime import datetime
from flask import Flask, render_template, redirect
from config import Config
from extensions import db, migrate, login_manager, socketio, limiter
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import login_required, current_user
from auth import bp as auth_bp

# ROUTES BLUEPRINTS
from routes.startups import bp as startups_bp, web_bp as startup_web_bp
from routes.opportunities import bp as opportunities_bp
from routes.applications import bp as applications_bp
from routes.referrals import bp as referrals_bp
from routes.admin import bp as admin_bp
from routes.meetings import bp as meetings_bp, web_bp as meetings_web_bp
from routes.notifications import bp as notifications_bp
from routes.messages import bp as messages_bp, web_bp as messages_web_bp
from routes.connections import bp as connections_bp

from routes.enablers import bp as enablers_bp
from routes.corporate import corporate_bp

# NEW: Payment and Messaging routes
# Payment routes temporarily disabled - razorpay integration removed
# from routes.payments import bp as payments_bp
from routes.messaging import bp as messaging_bp


# -----------------------------------------
# FLASK APP FACTORY
# -----------------------------------------
def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(Config)

    # Apply ProxyFix for Render/Production
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Initialize Sentry (must be done early)
    from sentry_config import init_sentry
    init_sentry(app)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    socketio.init_app(app)
    limiter.init_app(app)
    
    # Initialize Flask-Mail
    from extensions import mail
    mail.init_app(app)

    # Custom rate limit error handler
    @app.errorhandler(429)
    def ratelimit_handler(e):
        """Handle rate limit exceeded errors"""
        from flask import jsonify, request
        
        # Check if it's an API request
        if request.path.startswith('/api/'):
            return jsonify({
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
                "retry_after": e.description
            }), 429
        
        # For web requests, show a friendly page
        return render_template("429.html", retry_after=e.description), 429

    # Add custom Jinja2 filters
    @app.template_filter('strftime')
    def strftime_filter(date, format='%B %d, %Y at %I:%M %p'):
        """Custom strftime filter for Jinja2 templates"""
        if date:
            return date.strftime(format)
        return ""

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(startups_bp)
    app.register_blueprint(startup_web_bp)
    app.register_blueprint(opportunities_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(referrals_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(meetings_bp)
    app.register_blueprint(meetings_web_bp)
    app.register_blueprint(enablers_bp)
    app.register_blueprint(corporate_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(messages_web_bp)
    app.register_blueprint(connections_bp)
    
    # NEW: Payment and Messaging blueprints
    # Payment routes temporarily disabled - razorpay integration removed
    # app.register_blueprint(payments_bp)
    app.register_blueprint(messaging_bp)

    # Import WebRTC signaling events
    from routes import webrtc

    # -----------------------------------------
    # PAGE ROUTES (NO UI CHANGES)
    # -----------------------------------------

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/about")
    @app.route("/about.html")
    def about_page():
        return render_template("about.html")

    @app.route("/blog")
    @app.route("/blog.html")
    def blog_page():
        return render_template("blog.html")

    # Public Landing Pages
    @app.route("/innobridge")
    @app.route("/innobridge.html")
    @app.route("/enabler.html")
    def innobridge_landing():
        return render_template("enabler.html")

    # Auth Shortcuts
    @app.route("/login")
    @app.route("/login.html")
    @app.route("/templates/login")
    @app.route("/templates/login.html")
    def login_page():
        if current_user.is_authenticated:
            if current_user.role == "startup": return redirect("/startup")
            if current_user.role == "corporate": return redirect("/corporate")
            if current_user.role == "enabler": return redirect("/enabler")
            if current_user.role == "admin": return redirect("/admin")
            return redirect("/")
        return render_template("login.html")

    @app.route("/logout")
    def logout_page():
        return redirect("/auth/logout")

    @app.route("/startup-portal")
    @app.route("/startup_portal.html")
    def startup_portal_landing():
        return render_template("startup_portal.html")

    @app.route("/corporate.html")
    def corporate_landing():
        return render_template("corporate.html")

    # Auth Routes
    # Old login removed

    
    @app.route("/login-debug")
    def login_debug():
        return render_template("login_debug.html")

    @app.route("/signup")
    @app.route("/signup.html")
    def signup_page():
        return render_template("signup.html")

    @app.route("/register")
    def register_page():
        return render_template("signup.html")

    @app.route("/account-success")
    def account_success_page():
        from flask import request
        from models import User
        
        user_id = request.args.get('user_id')
        if not user_id:
            return redirect("/signup")
        
        user = User.query.get(user_id)
        if not user:
            return redirect("/signup")
        
        return render_template("account_success.html", user=user)

    @app.route("/dashboard")
    @app.route("/startup")
    @app.route("/startup_dashboard.html")
    @login_required
    def dashboard_page():
        # Only founders see this dashboard
        if current_user.role not in ("founder", "startup", "admin"):
            return render_template("403.html"), 403
        
        # Redirect to the new startup dashboard route
        return redirect('/startup/dashboard')





    @app.route("/corporate")
    @app.route("/corporate-dealflow")
    @login_required
    def corporate_dealflow_page():
        # Only corporate or admin
        if current_user.role not in ('corporate', 'admin'):
            return render_template("403.html"), 403

        from models import Startup
        
        # Real stats
        total_startups = Startup.query.count()
        recent_matches = Startup.query.order_by(Startup.created_at.desc()).limit(5).all()
        
        # Mock Deal Flow Value for now (or calculate if we had deal data)
        deal_flow_value = "$2.4M"
        
        return render_template("corporate_dashboard.html", 
                               total_startups=total_startups, 
                               recent_matches=recent_matches,
                               deal_flow_value=deal_flow_value)

    @app.route("/enabler")
    @login_required
    def enabler_page():
        if current_user.role not in ("enabler", "admin"):
            return render_template("403.html"), 403
        return render_template("enabler_dashboard.html")

    @app.route("/admin")
    @login_required
    def admin_page():
        if current_user.role != "admin":
            return render_template("403.html"), 403
        return render_template("admin_dashboard.html")

    @app.route("/admin/login")
    def admin_login_page():
        return render_template("admin_login.html")

    @app.route("/products")
    @app.route("/products.html")
    @app.route("/product.html")
    def products_page():
        return render_template("products.html")

    @app.route("/request-demo")
    @app.route("/request-demo")
    @app.route("/request_demo.html")
    @app.route("/request_demo")
    def request_demo_page():
        return render_template("request_demo.html")

    @app.route("/submit-demo", methods=["POST"])
    def submit_demo():
        from flask import request, redirect
        from models import Lead
        import json
        
        try:
            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")
            email = request.form.get("email")
            company = request.form.get("company")
            interest = request.form.get("interest")
            message = request.form.get("message")
            
            new_lead = Lead(
                type="demo",
                name=f"{first_name} {last_name}",
                email=email,
                company=company,
                subject=f"Demo Request: {interest}",
                message=message,
                extra_data=json.dumps({"interest": interest})
            )
            
            db.session.add(new_lead)
            db.session.commit()
        except Exception as e:
            print(f"Error saving demo lead: {e}")
            db.session.rollback()
            
        return render_template("thank_you.html")

    @app.route("/contact", methods=["GET", "POST"])
    @app.route("/contact.html", methods=["GET", "POST"])
    def contact_page():
        from flask import request, flash
        from models import ContactMessage, Lead
        
        if request.method == "POST":
            try:
                name = request.form.get("name")
                email = request.form.get("email")
                subject = request.form.get("subject")
                message = request.form.get("message")
                
                if not name or not email or not message:
                    flash("Please fill in all required fields.", "error")
                    return render_template("contact.html")
                
                # Save to Legacy Table
                contact_msg = ContactMessage(
                    name=name,
                    email=email,
                    subject=subject,
                    message=message
                )
                
                # Save to Unified Leads Table
                lead_entry = Lead(
                    type="contact",
                    name=name,
                    email=email,
                    subject=subject,
                    message=message
                )
                
                db.session.add(contact_msg)
                db.session.add(lead_entry)
                db.session.commit()
                
                flash("Thank you! Your message has been sent successfully.", "success")
                return redirect("/contact")
                
            except Exception as e:
                db.session.rollback()
                flash("An error occurred. Please try again later.", "error")
                print(f"Error sending message: {e}")
                
        return render_template("contact.html")

    # -----------------------------------------
    # MEETING ROUTES
    # -----------------------------------------
    @app.route("/meeting/join/<meeting_room_id>")
    @login_required
    def meeting_join_page(meeting_room_id):
        from models import Meeting, MeetingParticipant
        
        meeting = Meeting.query.filter_by(meeting_room_id=meeting_room_id).first_or_404()
        
        # Check if user has access
        participant = MeetingParticipant.query.filter_by(
            meeting_id=meeting.id,
            user_id=current_user.id
        ).first()
        
        # If not a participant, check if user is admin (admins can join any meeting)
        if not participant and current_user.role == "admin":
            # Create participant entry for admin user
            participant = MeetingParticipant(
                meeting_id=meeting.id,
                user_id=current_user.id,
                is_moderator=True  # Admins are always moderators
            )
            db.session.add(participant)
            try:
                db.session.commit()
            except Exception as e:
                print(f"Error adding admin as participant: {e}")
                db.session.rollback()
        
        if not participant:
            return render_template("403.html"), 403
        
        return render_template("meeting_join.html", meeting=meeting, participant=participant)

    @app.route("/meeting/room/<meeting_room_id>")
    @login_required
    def meeting_room_page(meeting_room_id):
        from models import Meeting, MeetingParticipant
        
        meeting = Meeting.query.filter_by(meeting_room_id=meeting_room_id).first_or_404()
        
        # Check if user has access
        participant = MeetingParticipant.query.filter_by(
            meeting_id=meeting.id,
            user_id=current_user.id
        ).first()
        
        # If not a participant, check if user is admin (admins can join any meeting)
        if not participant and current_user.role == "admin":
            # Create participant entry for admin user
            participant = MeetingParticipant(
                meeting_id=meeting.id,
                user_id=current_user.id,
                is_moderator=True  # Admins are always moderators
            )
            db.session.add(participant)
            try:
                db.session.commit()
            except Exception as e:
                print(f"Error adding admin as participant: {e}")
                db.session.rollback()
        
        if not participant:
            return render_template("403.html"), 403
        
        # Update participant status to joined
        participant.joined_at = datetime.utcnow()
        participant.attendance_status = "joined"
        db.session.commit()
        
        return render_template("meeting_room.html", meeting=meeting, participant=participant)

    @app.route("/admin/meetings")
    @login_required
    def admin_meetings_page():
        if current_user.role != "admin":
            return render_template("403.html"), 403
        return render_template("admin_meetings.html")

    @app.route("/test-meeting-inbox")
    @login_required
    def test_meeting_inbox():
        return render_template("test_meeting_inbox.html")

    # Opportunity listing page (public)
    @app.route("/opportunities")
    @app.route("/opportunities.html")
    @login_required
    def opportunities_page():
        return render_template("opportunities.html")

    # Startup profile page (founder only)
    # Startup profile route removed (merged with dashboard)

    # -----------------------------------------
    # ERROR HANDLERS
    # -----------------------------------------
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return redirect("/")

    @app.errorhandler(500)
    def server_error(e):
        return render_template("500.html"), 500

    return app


# -----------------------------------------
# MAIN ENTRY POINT
# -----------------------------------------
# Expose app globally for Gunicorn (Render default)
app = create_app()

if __name__ == "__main__":
    from extensions import socketio
    socketio.run(app, debug=True, port=5001, host='0.0.0.0')
