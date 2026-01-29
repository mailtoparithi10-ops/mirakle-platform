from flask import Blueprint, request, jsonify, redirect, session, url_for
from flask_login import login_required, current_user
from extensions import db
from models import Referral, User, Startup, Opportunity, Application
import json
from datetime import datetime
import uuid

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
# CONNECTOR: Generate a Shareable Link with QR Code
# ---------------------------------------
@bp.route("/generate-link", methods=["POST"])
@login_required
def generate_link():
    if current_user.role not in ("connector", "enabler"):
        return jsonify({"error": "Only connectors can generate referral links"}), 403

    data = request.json or {}
    opportunity_id = data.get("opportunity_id")
    
    if not opportunity_id:
        return jsonify({"error": "Missing opportunity_id"}), 400

    opp = Opportunity.query.get(opportunity_id)
    if not opp:
        return jsonify({"error": "Program not found"}), 404

    # Create a "link-based" referral placeholder
    token = str(uuid.uuid4())
    referral = Referral(
        connector_id=current_user.id,
        opportunity_id=opportunity_id,
        token=token,
        is_link_referral=True,
        status="pending_link", # New status for link-based
        startup_name="Link-based Lead",
        startup_email="pending@referral.link"
    )

    db.session.add(referral)
    db.session.commit()

    # The join URL
    join_url = url_for("referrals.join_via_link", token=token, _external=True)
    
    # QR Code data URL (will be generated on frontend)
    qr_data = join_url

    return jsonify({
        "success": True,
        "token": token,
        "join_url": join_url,
        "qr_data": qr_data,
        "opportunity_title": opp.title,
        "referral_id": referral.id,
        "referral": referral.to_dict()
    })

# ---------------------------------------
# STARTUP: Join via Link (Track Click)
# ---------------------------------------
@bp.route("/join/<token>", methods=["GET"])
def join_via_link(token):
    from models import ReferralClick
    
    referral = Referral.query.filter_by(token=token).first_or_404()
    
    # Track the click
    click = ReferralClick(
        referral_id=referral.id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', '')[:500],
        viewed_opportunity=False,
        applied=False
    )
    db.session.add(click)
    
    # Update referral status if it's still pending_link
    if referral.status == "pending_link":
        referral.status = "link_clicked"
    
    db.session.commit()
    
    # Store referral info in session
    session['referral_token'] = token
    session['referral_id'] = referral.id
    session['opportunity_id'] = referral.opportunity_id
    
    # Redirect to login with referral context
    return redirect(f"/login?ref={token}")

# ---------------------------------------
# STARTUP: List Incoming Referrals
# ---------------------------------------
@bp.route("/incoming", methods=["GET"])
@login_required
def list_incoming_referrals():
    if current_user.role not in ("founder", "startup", "admin"):
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
    if current_user.role not in ("founder", "startup", "admin"):
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


# ---------------------------------------
# CONNECTOR: Get Referral Link Statistics
# ---------------------------------------
@bp.route("/link-stats/<int:referral_id>", methods=["GET"])
@login_required
def get_link_stats(referral_id):
    from models import ReferralClick
    
    if current_user.role not in ("connector", "enabler", "admin"):
        return jsonify({"error": "Forbidden"}), 403

    referral = Referral.query.get_or_404(referral_id)
    
    # Security check: must be the connector who created it (or admin)
    if current_user.role != "admin" and referral.connector_id != current_user.id:
        return jsonify({"error": "Not your referral"}), 403

    # Get click statistics
    clicks = ReferralClick.query.filter_by(referral_id=referral_id).all()
    
    total_clicks = len(clicks)
    unique_users = len(set([c.user_id for c in clicks if c.user_id]))
    viewed_count = sum([1 for c in clicks if c.viewed_opportunity])
    applied_count = sum([1 for c in clicks if c.applied])
    
    # Get opportunity details
    opp = Opportunity.query.get(referral.opportunity_id)
    
    # Get application if exists
    application = None
    if referral.startup_id:
        app = Application.query.filter_by(
            startup_id=referral.startup_id,
            opportunity_id=referral.opportunity_id
        ).first()
        if app:
            application = app.to_dict()
    
    return jsonify({
        "success": True,
        "referral": referral.to_dict(),
        "opportunity": opp.to_dict() if opp else None,
        "application": application,
        "stats": {
            "total_clicks": total_clicks,
            "unique_users": unique_users,
            "viewed_opportunity": viewed_count,
            "applied": applied_count,
            "conversion_rate": (applied_count / total_clicks * 100) if total_clicks > 0 else 0
        },
        "clicks": [c.to_dict() for c in clicks]
    })
