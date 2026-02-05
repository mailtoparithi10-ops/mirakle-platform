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
    
    # Notify Opportunity Owner and Administrators
    try:
        from models import Notification, User
        opp = Opportunity.query.get(opportunity_id)
        
        # 1. Notify the Opportunity Owner (e.g., Corporate User)
        if opp and opp.owner_id:
            notif = Notification(
                user_id=opp.owner_id,
                title="New Application Received",
                message=f"Startup {startup.name} has applied to your program: {opp.title}",
                type="success",
                link=f"/corporate#applications"
            )
            db.session.add(notif)
        
        # 2. Notify all Administrators
        admins = User.query.filter_by(role="admin").all()
        for admin in admins:
            # Skip if admin is also the owner to avoid double notification
            if opp and admin.id == opp.owner_id:
                continue
                
            admin_notif = Notification(
                user_id=admin.id,
                title="Program Application Alert",
                message=f"New application from {startup.name} for {opp.title if opp else 'Program ID ' + str(opportunity_id)}",
                type="info",
                link=f"/admin#programs"
            )
            db.session.add(admin_notif)
            
    except Exception as e:
        print(f"Notification error: {e}")

    db.session.commit()

    return jsonify(app_entry.to_dict()), 201


# ---------------------------------------
# UPDATE APPLICATION STATUS (Admin Only)
# ---------------------------------------
@bp.route("/<int:id>/status", methods=["PUT"])
@login_required
def update_status(id):
    if current_user.role != "admin":
        return jsonify({"error": "forbidden", "message": "Only administrators can update application status"}), 403

    app_entry = Application.query.get_or_404(id)
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
# GET ALL APPLICATIONS OF AN OPPORTUNITY (Admin Only)
# ---------------------------------------
@bp.route("/opportunity/<int:opportunity_id>", methods=["GET"])
@login_required
def list_for_opportunity(opportunity_id):
    if current_user.role != "admin":
        return jsonify({"error": "forbidden", "message": "Only administrators can view opportunity applications"}), 403

    opp = Opportunity.query.get_or_404(opportunity_id)
    items = Application.query.filter_by(opportunity_id=opportunity_id).all()
    return jsonify([i.to_dict() for i in items])


# ---------------------------------------
# FOUNDER VIEW: SEE APPLICATIONS OF YOUR STARTUPS
# ---------------------------------------
@bp.route("/mine", methods=["GET"])
@login_required
def my_applications():
    if current_user.role not in ("founder", "startup", "admin"):
        return jsonify({"error": "forbidden"}), 403

    # Get all startups of founder
    startup_ids = [s.id for s in current_user.startups]

    items = Application.query.filter(Application.startup_id.in_(startup_ids)).all() if startup_ids else []

    results = []
    for i in items:
        d = i.to_dict()
        # Add extra info for UI
        startup = Startup.query.get(i.startup_id)
        opp = Opportunity.query.get(i.opportunity_id)
        d["startup_name"] = startup.name if startup else "Unknown"
        d["opportunity_title"] = opp.title if opp else "Unknown"
        results.append(d)

    return jsonify(results)


# ---------------------------------------
# CORPORATE VIEW: SEE ALL APPLICATIONS SENT TO YOUR PROGRAMS (Read Only)
# ---------------------------------------
@bp.route("/corporate/all", methods=["GET"])
@login_required
def list_for_corporate():
    if current_user.role != "corporate" and current_user.role != "admin":
        return jsonify({"error": "forbidden"}), 403

    # Corporate users can only view applications, not manage them
    # Get all opportunities owned by this user
    opps = Opportunity.query.filter_by(owner_id=current_user.id).all()
    opp_ids = [o.id for o in opps]

    if not opp_ids:
        return jsonify([])

    items = Application.query.filter(Application.opportunity_id.in_(opp_ids)).all()

    results = []
    for i in items:
        d = i.to_dict()
        startup = Startup.query.get(i.startup_id)
        opp = Opportunity.query.get(i.opportunity_id)
        d["startup_name"] = startup.name if startup else "Unknown"
        d["opportunity_title"] = opp.title if opp else "Unknown"
        d["read_only"] = True  # Indicate this is read-only for corporate users
        results.append(d)

    return jsonify(results)
