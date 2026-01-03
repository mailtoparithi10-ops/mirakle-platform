# routes/referrals.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Referral, Startup, Opportunity
import json, datetime

bp = Blueprint("referrals", __name__, url_prefix="/api/referrals")


# ---------------------------------------
# CONNECTOR CREATES A REFERRAL
# ---------------------------------------
@bp.route("/", methods=["POST"])
@login_required
def create_referral():
    if current_user.role not in ("connector", "admin"):
        return jsonify({"error": "forbidden"}), 403

    data = request.json or request.form or {}

    startup_id = data.get("startup_id")
    opportunity_id = data.get("opportunity_id")

    if not startup_id or not opportunity_id:
        return jsonify({"error": "startup_id and opportunity_id required"}), 400

    Startup.query.get_or_404(startup_id)
    Opportunity.query.get_or_404(opportunity_id)

    ref = Referral(
        connector_id=current_user.id,
        startup_id=startup_id,
        opportunity_id=opportunity_id,
        status="open",
        reward_log=json.dumps([])
    )

    db.session.add(ref)
    db.session.commit()

    return jsonify(ref.to_dict()), 201


# ---------------------------------------
# CONNECTOR VIEWS THEIR REFERRALS
# ---------------------------------------
@bp.route("/mine", methods=["GET"])
@login_required
def my_referrals():
    if current_user.role not in ("connector", "admin"):
        return jsonify({"error": "forbidden"}), 403

    items = Referral.query.filter_by(connector_id=current_user.id).all()
    return jsonify([i.to_dict() for i in items])


# ---------------------------------------
# CORPORATE / ADMIN UPDATES REFERRAL STATUS
# ---------------------------------------
@bp.route("/<int:id>/status", methods=["PUT"])
@login_required
def update_status(id):
    ref = Referral.query.get_or_404(id)
    opp = Opportunity.query.get_or_404(ref.opportunity_id)

    # Only the opportunity owner (corporate) or admin can update
    if current_user.id != opp.owner_id and current_user.role != "admin":
        return jsonify({"error": "forbidden"}), 403

    data = request.json or request.form or {}

    new_status = data.get("status")
    note = data.get("note")

    if not new_status:
        return jsonify({"error": "status required"}), 400

    # Update status (open, successful, failed)
    ref.status = new_status

    # Append to reward log
    reward_log = json.loads(ref.reward_log or "[]")
    reward_log.append({
        "status": new_status,
        "note": note,
        "at": datetime.datetime.utcnow().isoformat(),
        "by": current_user.id
    })
    ref.reward_log = json.dumps(reward_log)

    db.session.commit()

    return jsonify(ref.to_dict())


# ---------------------------------------
# ADMIN VIEW: ALL REFERRALS (OPTIONAL)
# ---------------------------------------
@bp.route("/all", methods=["GET"])
@login_required
def all_referrals():
    if current_user.role != "admin":
        return jsonify({"error": "forbidden"}), 403

    items = Referral.query.all()
    return jsonify([i.to_dict() for i in items])
