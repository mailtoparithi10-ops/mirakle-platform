from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Referral, User, Startup, Opportunity
import json
from datetime import datetime

bp = Blueprint("referrals", __name__, url_prefix="/api/referrals")

# ---------------------------------------
# CONNECTOR: Create a Referral
# ---------------------------------------
@bp.route("/", methods=["POST"])
@login_required
def create_referral():
    if current_user.role != "connector":
        return jsonify({"error": "Only connectors can create referrals"}), 403

    data = request.json or {}
    startup_name = data.get("startup_name")
    startup_email = data.get("startup_email")
    opportunity_id = data.get("opportunity_id")
    notes = data.get("notes")

    if not startup_name or not startup_email or not opportunity_id:
        return jsonify({"error": "Missing required fields"}), 400

    # Check if opportunity exists
    opp = Opportunity.query.get(opportunity_id)
    if not opp:
        return jsonify({"error": "Program not found"}), 404

    # Try to find existing startup user
    user = User.query.filter_by(email=startup_email).first()
    startup_id = None
    if user and user.role == "founder" and user.startups:
        startup_id = user.startups[0].id

    referral = Referral(
        connector_id=current_user.id,
        startup_id=startup_id,
        opportunity_id=opportunity_id,
        startup_name=startup_name,
        startup_email=startup_email,
        notes=notes,
        status="pending"
    )

    db.session.add(referral)
    db.session.commit()

    return jsonify({
        "success": True, 
        "message": "Referral request sent to startup.",
        "referral": referral.to_dict()
    }), 201

# ---------------------------------------
# STARTUP: List Incoming Referrals
# ---------------------------------------
@bp.route("/incoming", methods=["GET"])
@login_required
def list_incoming_referrals():
    if current_user.role != "founder":
        return jsonify({"error": "Only startups can see incoming referrals"}), 403

    # Find all referrals where startup_email matches current_user.email
    referrals = Referral.query.filter_by(startup_email=current_user.email).all()
    
    # Enrich with opportunity and connector details
    results = []
    for r in referrals:
        d = r.to_dict()
        opp = Opportunity.query.get(r.opportunity_id)
        conn = User.query.get(r.connector_id)
        d['opportunity_title'] = opp.title if opp else "Unknown Program"
        d['connector_name'] = conn.name if conn else "Unknown Connector"
        results.append(d)

    return jsonify({"success": True, "referrals": results})

# ---------------------------------------
# STARTUP: Accept / Reject Referral
# ---------------------------------------
@bp.route("/<int:id>/action", methods=["POST"])
@login_required
def referral_action(id):
    if current_user.role != "founder":
        return jsonify({"error": "Action forbidden"}), 403

    referral = Referral.query.get_or_404(id)
    
    # Security check: must match email
    if referral.startup_email != current_user.email:
        return jsonify({"error": "This referral is not for you"}), 403

    data = request.json or {}
    action = data.get("action") # 'accept' or 'reject'

    if action == 'accept':
        referral.status = 'accepted'
        # Link startup_id if not already linked
        if not referral.startup_id and current_user.startups:
            referral.startup_id = current_user.startups[0].id
    elif action == 'reject':
        referral.status = 'rejected'
    elif action == 'review':
        referral.status = 'under_review'
    elif action == 'shortlist':
        referral.status = 'shortlisted'
    else:
        return jsonify({"error": "Invalid action"}), 400

    db.session.commit()
    return jsonify({"success": True, "message": f"Referral {action}ed."})

# ---------------------------------------
# CONNECTOR: List My Referrals
# ---------------------------------------
@bp.route("/my", methods=["GET"])
@login_required
def list_my_referrals():
    if current_user.role != "connector":
        return jsonify({"error": "Forbidden"}), 403

    referrals = Referral.query.filter_by(connector_id=current_user.id).all()
    results = []
    for r in referrals:
        d = r.to_dict()
        opp = Opportunity.query.get(r.opportunity_id)
        d['opportunity_title'] = opp.title if opp else "Unknown Program"
        d['opportunity_owner'] = opp.owner_company if opp else "Unknown Corporate"
        
        # Cross-reference with Applications if startup_id exists
        app_status = None
        if r.startup_id:
            app = Application.query.filter_by(startup_id=r.startup_id, opportunity_id=r.opportunity_id).first()
            if app:
                app_status = app.status
        
        d['application_status'] = app_status # This is the corporate-assigned status
        results.append(d)

    return jsonify({"success": True, "referrals": results})

# ---------------------------------------
# ADMIN: List Confirmed Referrals
# ---------------------------------------
@bp.route("/admin", methods=["GET"])
@login_required
def admin_list_referrals():
    if current_user.role != "admin":
        return jsonify({"error": "Admin access required"}), 403

    # Show only accepted (confirmed by startup) or further
    referrals = Referral.query.filter(Referral.status != 'pending').all()
    
    results = []
    for r in referrals:
        d = r.to_dict()
        opp = Opportunity.query.get(r.opportunity_id)
        conn = User.query.get(r.connector_id)
        d['opportunity_title'] = opp.title if opp else "Unknown Program"
        d['connector_name'] = conn.name if conn else "Unknown Connector"
        results.append(d)

    return jsonify({"success": True, "referrals": results})
