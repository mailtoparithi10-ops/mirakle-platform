# routes/applications.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Application, Startup, Opportunity
import json, datetime

bp = Blueprint("applications", __name__, url_prefix="/api/applications")


# ---------------------------------------
# CREATE APPLICATION (Founder)
# ---------------------------------------
@bp.route("/", methods=["POST"])
@login_required
def create_application():
    data = request.json or request.form or {}

    startup_id = data.get("startup_id")
    opportunity_id = data.get("opportunity_id")

    if not (startup_id and opportunity_id):
        return jsonify({"error": "startup_id and opportunity_id required"}), 400

    # Validate startup belongs to the founder unless admin
    startup = Startup.query.get_or_404(startup_id)
    if current_user.role != "admin" and startup.founder_id != current_user.id:
        return jsonify({"error": "forbidden"}), 403

    # Check opportunity exists
    Opportunity.query.get_or_404(opportunity_id)

    # Create initial timeline entry
    timeline = [{
        "status": "submitted",
        "note": "Application submitted",
        "at": datetime.datetime.utcnow().isoformat(),
        "by": current_user.id
    }]

    app_entry = Application(
        startup_id=startup_id,
        opportunity_id=opportunity_id,
        applied_by_id=current_user.id,
        status="submitted",
        timeline=json.dumps(timeline),
        notes=json.dumps([])
    )

    db.session.add(app_entry)
    db.session.commit()

    return jsonify(app_entry.to_dict()), 201


# ---------------------------------------
# UPDATE APPLICATION STATUS (Corporate / Admin)
# ---------------------------------------
@bp.route("/<int:id>/status", methods=["PUT"])
@login_required
def update_status(id):
    app_entry = Application.query.get_or_404(id)
    opp = Opportunity.query.get_or_404(app_entry.opportunity_id)

    # Only opportunity owner or admin may update
    if current_user.id != opp.owner_id and current_user.role != "admin":
        return jsonify({"error": "forbidden"}), 403

    data = request.json or request.form or {}

    new_status = data.get("status")
    note = data.get("note", "")

    if not new_status:
        return jsonify({"error": "status required"}), 400

    # Update status
    app_entry.status = new_status

    # Append to timeline
    timeline = json.loads(app_entry.timeline or "[]")
    timeline.append({
        "status": new_status,
        "note": note,
        "at": datetime.datetime.utcnow().isoformat(),
        "by": current_user.id
    })
    app_entry.timeline = json.dumps(timeline)

    db.session.commit()

    return jsonify(app_entry.to_dict())


# ---------------------------------------
# GET ALL APPLICATIONS OF AN OPPORTUNITY (Corporate only)
# ---------------------------------------
@bp.route("/opportunity/<int:opportunity_id>", methods=["GET"])
@login_required
def list_for_opportunity(opportunity_id):
    opp = Opportunity.query.get_or_404(opportunity_id)

    # Only corporate owner or admin
    if current_user.id != opp.owner_id and current_user.role != "admin":
        return jsonify({"error": "forbidden"}), 403

    items = Application.query.filter_by(opportunity_id=opportunity_id).all()
    return jsonify([i.to_dict() for i in items])


# ---------------------------------------
# FOUNDER VIEW: SEE APPLICATIONS OF YOUR STARTUPS
# ---------------------------------------
@bp.route("/mine", methods=["GET"])
@login_required
def my_applications():
    if current_user.role not in ("founder", "admin"):
        return jsonify({"error": "forbidden"}), 403

    # Get all startups of founder
    startup_ids = [s.id for s in current_user.startups]

    items = Application.query.filter(
        Application.startup_id.in_(startup_ids)
    ).all()

    return jsonify([i.to_dict() for i in items])
