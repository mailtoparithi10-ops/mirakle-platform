# routes/admin.py
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from extensions import db
from models import User, Startup, Opportunity, Application, Referral

bp = Blueprint("admin", __name__, url_prefix="/api/admin")


# Admin authorization helper
def require_admin():
    if not current_user.is_authenticated or current_user.role != "admin":
        return jsonify({"error": "forbidden"}), 403


# ---------------------------------------
# GLOBAL METRICS
# ---------------------------------------
@bp.route("/metrics", methods=["GET"])
@login_required
def metrics():
    if require_admin():
        return require_admin()

    return jsonify({
        "total_users": User.query.count(),
        "total_startups": Startup.query.count(),
        "total_opportunities": Opportunity.query.count(),
        "total_applications": Application.query.count(),
        "total_referrals": Referral.query.count(),
        "countries": list({u.country for u in User.query.all() if u.country})
    })


# ---------------------------------------
# GET ALL USERS
# ---------------------------------------
@bp.route("/users", methods=["GET"])
@login_required
def get_users():
    if require_admin():
        return require_admin()

    users = User.query.all()
    return jsonify([u.to_dict() for u in users])


# ---------------------------------------
# BAN USER
# ---------------------------------------
@bp.route("/ban/<int:id>", methods=["PUT"])
@login_required
def ban_user(id):
    if require_admin():
        return require_admin()

    user = User.query.get_or_404(id)
    user.is_active = False
    db.session.commit()
    return jsonify({"message": "user banned", "user": user.to_dict()})


# ---------------------------------------
# UNBAN USER
# ---------------------------------------
@bp.route("/unban/<int:id>", methods=["PUT"])
@login_required
def unban_user(id):
    if require_admin():
        return require_admin()

    user = User.query.get_or_404(id)
    user.is_active = True
    db.session.commit()
    return jsonify({"message": "user unbanned", "user": user.to_dict()})


# ---------------------------------------
# DELETE USER
# ---------------------------------------
@bp.route("/users/<int:id>", methods=["DELETE"])
@login_required
def delete_user(id):
    if require_admin():
        return require_admin()

    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "user deleted"})


# ---------------------------------------
# UPDATE USER
# ---------------------------------------
@bp.route("/users/<int:id>", methods=["PUT"])
@login_required
def update_user(id):
    if require_admin():
        return require_admin()

    user = User.query.get_or_404(id)
    data = request.get_json()

    if "name" in data:
        user.name = data["name"]
    if "email" in data:
        user.email = data["email"]
    if "role" in data:
        user.role = data["role"]
    
    db.session.commit()
    return jsonify({"message": "user updated", "user": user.to_dict()})
