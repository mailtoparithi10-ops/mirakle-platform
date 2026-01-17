# app.py (NEW CLEAN BACKEND)
import os
from flask import Flask, render_template, redirect
from config import Config
from extensions import db, migrate, login_manager
from flask_login import login_required, current_user
from auth import bp as auth_bp

# ROUTES BLUEPRINTS
from routes.startups import bp as startups_bp
from routes.opportunities import bp as opportunities_bp
from routes.applications import bp as applications_bp
from routes.referrals import bp as referrals_bp
from routes.admin import bp as admin_bp


# -----------------------------------------
# FLASK APP FACTORY
# -----------------------------------------
def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(Config)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(startups_bp)
    app.register_blueprint(opportunities_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(referrals_bp)
    app.register_blueprint(admin_bp)

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
    @app.route("/connector.html")
    def innobridge_landing():
        return render_template("connector.html")

    # Auth Shortcuts
    @app.route("/login")
    @app.route("/login.html")
    @app.route("/templates/login")
    @app.route("/templates/login.html")
    def login_page():
        if current_user.is_authenticated:
            if current_user.role == "startup": return redirect("/startup")
            if current_user.role == "corporate": return redirect("/corporate")
            if current_user.role == "connector": return redirect("/connector")
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

    @app.route("/dashboard")
    @app.route("/startup")
    @app.route("/startup_dashboard.html")
    @login_required
    def dashboard_page():
        # Only founders see this dashboard
        if current_user.role != "founder" and current_user.role != "startup" and current_user.role != "admin":
            return render_template("403.html"), 403
        return render_template("startup_dashboard.html")

    @app.route("/investor")
    def investor_page():
        return render_template("investor.html")



    @app.route("/corporate")
    @app.route("/corporate-dealflow")
    def corporate_dealflow_page():
        return render_template("corporate_dashboard.html")

    @app.route("/connector")
    @login_required
    def connector_page():
        if current_user.role not in ("connector", "admin"):
            return render_template("403.html"), 403
        return render_template("connector_dashboard.html")

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
    def request_demo_page():
        return render_template("request_demo.html")

    @app.route("/submit-demo", methods=["POST"])
    def submit_demo():
        # In a real app, we would save this to DB or send email
        return render_template("thank_you.html")

    @app.route("/contact")
    @app.route("/contact.html")
    def contact_page():
        return render_template("contact.html")

    # Opportunity listing page (public)
    @app.route("/opportunities")
    @app.route("/opportunities.html")
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
        return render_template("404.html"), 404

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
    app.run(debug=True, port=5001)
