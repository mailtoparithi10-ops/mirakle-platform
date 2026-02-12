# routes/admin.py
from flask import Blueprint, jsonify, request, current_app, Response
from flask_login import login_required, current_user
from extensions import db
from models import User, Startup, Opportunity, Application, Referral
from admin_analytics_service import AdminAnalyticsService
import json
from datetime import datetime
import os
from werkzeug.utils import secure_filename

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

    from models import Lead
    return jsonify({
        "total_users": User.query.count(),
        "total_startups": User.query.filter_by(role='startup').count() + User.query.filter_by(role='founder').count(),
        "total_corporate": User.query.filter_by(role='corporate').count(),
        "total_connectors": User.query.filter_by(role='connector').count() + User.query.filter_by(role='enabler').count(),
        "total_opportunities": Opportunity.query.count(),
        "total_applications": Application.query.count(),
        "total_referrals": Referral.query.count(),
        "total_leads": Lead.query.count(),
        "countries": list({u.country for u in User.query.all() if u.country})
    })

@bp.route("/stats", methods=["GET"])
@login_required
def get_stats():
    if require_admin():
        return require_admin()
        
    from models import Lead
    stats = {
        "total_users": User.query.count(),
        "total_startups": User.query.filter_by(role='startup').count() + User.query.filter_by(role='founder').count(),
        "total_corporate": User.query.filter_by(role='corporate').count(),
        "total_connectors": User.query.filter_by(role='connector').count() + User.query.filter_by(role='enabler').count(),
        "total_programs": Opportunity.query.count(),
        "total_applications": Application.query.count(),
        "total_referrals": Referral.query.count(),
        "total_leads": Lead.query.count(),
        "total_admins": User.query.filter_by(role='admin').count()
    }
    
    return jsonify({"success": True, "stats": stats})


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
# GET ALL LEADS (Inquiries, Demos, Investors)
# ---------------------------------------
@bp.route("/leads", methods=["GET"])
@login_required
def get_leads():
    if require_admin():
        return require_admin()

    from models import Lead
    leads = Lead.query.order_by(Lead.created_at.desc()).all()
    return jsonify([l.to_dict() for l in leads])


@bp.route("/leads/<int:id>/read", methods=["PUT"])
@login_required
def mark_lead_read(id):
    if require_admin():
        return require_admin()

    from models import Lead
    lead = Lead.query.get_or_404(id)
    lead.is_read = True
    db.session.commit()
    return jsonify({"success": True})


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
# GET ALL OPPORTUNITIES (PROGRAMS)
# ---------------------------------------
@bp.route("/opportunities", methods=["GET"])
@login_required
def get_opportunities():
    if require_admin():
        return require_admin()

    opps = Opportunity.query.all()
    return jsonify({"success": True, "opportunities": [o.to_dict() for o in opps]})


# ---------------------------------------
# CREATE OPPORTUNITY (Admin Only)
# ---------------------------------------
@bp.route("/opportunities", methods=["POST"])
@login_required
def create_opportunity():
    if require_admin():
        return require_admin()

    data = request.json or request.form or {}

    opp = Opportunity(
        owner_id=current_user.id,
        title=data.get("title"),
        type=data.get("type"),
        description=data.get("description"),
        eligibility=data.get("eligibility"),
        sectors=json.dumps(data.get("sectors", [])),
        target_stages=json.dumps(data.get("target_stages", [])),
        countries=json.dumps(data.get("countries", [])),
        deadline=datetime.fromisoformat(data["deadline"]) if data.get("deadline") else None,
        benefits=data.get("benefits"),
        banner_url=data.get("banner_url"),
        status=data.get("status", "draft"),
    )

    db.session.add(opp)
    db.session.commit()

    return jsonify({"success": True, "opportunity": opp.to_dict()}), 201


# ---------------------------------------
# UPDATE OPPORTUNITY (Admin Only)
# ---------------------------------------
@bp.route("/opportunities/<int:id>", methods=["PUT"])
@login_required
def update_opportunity(id):
    if require_admin():
        return require_admin()

    opp = Opportunity.query.get_or_404(id)
    data = request.json or request.form or {}

    # Update simple fields
    for key in ["title", "type", "description", "eligibility", "benefits", "status", "banner_url"]:
        if key in data:
            setattr(opp, key, data[key])

    # Update JSON fields
    if "sectors" in data:
        opp.sectors = json.dumps(data["sectors"])
    if "target_stages" in data:
        opp.target_stages = json.dumps(data["target_stages"])
    if "countries" in data:
        opp.countries = json.dumps(data["countries"])

    # Update deadline
    if data.get("deadline"):
        opp.deadline = datetime.fromisoformat(data["deadline"])

    db.session.commit()

    return jsonify({"success": True, "opportunity": opp.to_dict()})


# ---------------------------------------
# DELETE OPPORTUNITY (Admin Only)
# ---------------------------------------
@bp.route("/opportunities/<int:id>", methods=["DELETE"])
@login_required
def delete_opportunity(id):
    if require_admin():
        return require_admin()

    opp = Opportunity.query.get_or_404(id)
    db.session.delete(opp)
    db.session.commit()

    return jsonify({"success": True, "message": "Opportunity deleted successfully"})


# ---------------------------------------
# GET ALL APPLICATIONS (Admin Only)
# ---------------------------------------
@bp.route("/applications", methods=["GET"])
@login_required
def get_all_applications():
    if require_admin():
        return require_admin()

    applications = Application.query.order_by(Application.created_at.desc()).all()
    results = []
    
    for app in applications:
        d = app.to_dict()
        startup = Startup.query.get(app.startup_id)
        opp = Opportunity.query.get(app.opportunity_id)
        d["startup_name"] = startup.name if startup else "Unknown"
        d["opportunity_title"] = opp.title if opp else "Unknown"
        results.append(d)

    return jsonify({"success": True, "applications": results})


# ---------------------------------------
# UPDATE APPLICATION STATUS (Admin Only)
# ---------------------------------------
@bp.route("/applications/<int:id>/status", methods=["PUT"])
@login_required
def update_application_status(id):
    if require_admin():
        return require_admin()

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
        "at": datetime.utcnow().isoformat(),
        "by": current_user.id
    })
    app_entry.timeline = json.dumps(timeline)

    db.session.commit()

    return jsonify({"success": True, "application": app_entry.to_dict()})


# ---------------------------------------
# GET ALL REFERRALS
# ---------------------------------------
@bp.route("/referrals", methods=["GET"])
@login_required
def get_referrals():
    if require_admin():
        return require_admin()

    referrals = Referral.query.order_by(Referral.created_at.desc()).all()
    results = []
    
    for ref in referrals:
        connector = User.query.get(ref.connector_id)
        startup = Startup.query.get(ref.startup_id)
        program = Opportunity.query.get(ref.opportunity_id)
        
        # Get startup name (Startup model might not have company_name, check User)
        # Assuming Startup model has a OneToOne with User or fields. 
        # Let's check models.py again for Startup field if needed, but for now we'll assume it's linked or has fields.
        # Actually, looking at models.py earlier, Startup is a model.
        # Let's double check Startup model to be safe.
        
        # Re-fetching for safety in this loop
        connector_name = connector.name if connector else "Unknown"
        
        # Startup Name: The Startup model usually links to a User or has its own name.
        # Based on previous knowledge, Startup might use 'user.company' or similar. 
        # Let's look at how Startup is defined.
        
        startup_name = "Unknown Startup"
        if startup:
             if hasattr(startup, 'name'):
                 startup_name = startup.name
             elif hasattr(startup, 'company_name'):
                 startup_name = startup.company_name
             elif hasattr(startup, 'founder') and startup.founder:
                 startup_name = startup.founder.company

        program_title = program.title if program else "Unknown Program"
        
        results.append({
            "id": ref.id,
            "connector_name": connector_name,
            "startup_id": ref.startup_id, # return ID just in case
            "startup_name": startup_name,
            "program_title": program_title,
            "status": ref.status,
            "created_at": ref.created_at.isoformat()
        })

    return jsonify({"success": True, "referrals": results})

# ---------------------------------------
# SEED ALL DATA (MOCK USERS & PROGRAMS)
# ---------------------------------------
@bp.route("/seed-all-data", methods=["POST"])
@login_required
def seed_all_data():
    if require_admin():
        return require_admin()
        
    from datetime import datetime, timedelta
    import random
    
    # 1. SEED MOCK USERS (Startup, Corporate, Connector)
    mock_users = [
        {"name": "Sarah Chen", "email": "sarah@futuretech.io", "role": "startup", "company": "FutureTech AI", "country": "Singapore"},
        {"name": "Marcello Silva", "email": "m.silva@greenpulse.com", "role": "startup", "company": "GreenPulse", "country": "Brazil"},
        {"name": "Alex Rivet", "email": "alex@nexus.vc", "role": "connector", "company": "Nexus Ventures", "country": "France"},
        {"name": "Elena Popova", "email": "e.popova@innovate.ru", "role": "connector", "company": "Innovate Hub", "country": "Russia"},
        {"name": "James Wilson", "email": "j.wilson@megacorp.com", "role": "corporate", "company": "MegaCorp Global", "country": "USA"},
        {"name": "Yuki Tanaka", "email": "tanaka@softbank-demo.jp", "role": "corporate", "company": "SoftBank Innovation", "country": "Japan"},
        {"name": "Founder One", "email": "founder1@test.com", "role": "founder", "company": "Test Startup", "country": "Germany"},
        {"name": "Enabler Pro", "email": "pro@enabler.io", "role": "enabler", "company": "Startup Enablers", "country": "UK"}
    ]
    
    users_added = 0
    for u in mock_users:
        if not User.query.filter_by(email=u["email"]).first():
            new_user = User(
                name=u["name"],
                email=u["email"],
                role=u["role"],
                company=u["company"],
                country=u["country"]
            )
            new_user.set_password("password123")
            db.session.add(new_user)
            users_added += 1
    
    # 2. SEED MOCK PROGRAMS
    # Only if no programs exist or we want to force more
    mock_programs = [
        {
            "title": "Global Fintech Accelerator 2026",
            "type": "accelerator",
            "description": "A 3-month program for early-stage fintech startups focusing on cross-border payments.",
            "benefits": "$50k equity-free grant + mentorship",
            "status": "published",
            "banner_url": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?q=80&w=1965&auto=format&fit=crop"
        },
        {
            "title": "Sustainability Innovation Grant",
            "type": "grant",
            "description": "Government-backed grant for startups working on carbon sequestration technologies.",
            "benefits": "Up to $100k non-dilutive funding",
            "status": "published",
            "banner_url": "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?q=80&w=2070&auto=format&fit=crop"
        },
        {
            "title": "Retail Tech Pilot - MegaCorp",
            "type": "pilot",
            "description": "MegaCorp is scouting for AI solutions to optimize supply chain logistics for their retail outlets.",
            "benefits": "Paid PoC + distribution opportunity",
            "status": "published",
            "banner_url": "https://images.unsplash.com/photo-1556742049-0cfed4f7a07d?q=80&w=2070&auto=format&fit=crop"
        },
        {
            "title": "HealthTech Challenge APAC",
            "type": "challenge",
            "description": "Solving regional healthcare accessibility through mobile-first digital solutions.",
            "benefits": "Pilot with regional hospital networks",
            "status": "published",
            "banner_url": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?q=80&w=2070&auto=format&fit=crop"
        },
        {
            "title": "DeepTech Pioneer Program",
            "type": "accelerator",
            "description": "Unlocking breakthroughs in quantum computing and material sciences.",
            "benefits": "Lab access + $100k investment",
            "status": "published",
            "banner_url": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?q=80&w=2070&auto=format&fit=crop"
        },
        {
            "title": "Web3 Innovation Grant",
            "type": "grant",
            "description": "Building the future of decentralized finance and identity on the blockchain.",
            "benefits": "$25k non-equity grant",
            "status": "published",
            "banner_url": "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?q=80&w=2070&auto=format&fit=crop"
        },
        {
            "title": "AgriTech Smart Farming Initiative",
            "type": "pilot",
            "description": "Scouting for IoT and AI solutions to optimize crop yields and reduce waste in agriculture.",
            "benefits": "Implementation pilot + $40k funding",
            "status": "published",
            "banner_url": "https://images.unsplash.com/photo-1628352081506-83c43123ed6d?q=80&w=2071&auto=format&fit=crop"
        },
        {
            "title": "EdTech Catalyst Program",
            "type": "accelerator",
            "description": "Bridging the digital divide with innovative remote learning tools for rural schools.",
            "benefits": "Mentorship + $30h grant",
            "status": "published",
            "banner_url": "https://images.unsplash.com/photo-1509062522246-3755977927d7?q=80&w=2070&auto=format&fit=crop"
        },
        {
            "title": "ClimateTech Carbon Challenge",
            "type": "challenge",
            "description": "Scouting for high-impact carbon capture and sequestration technologies.",
            "benefits": "$500k prize pool + pilot opportunity",
            "status": "published",
            "banner_url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?q=80&w=2070&auto=format&fit=crop"
        },
        {
            "title": "SpaceTech Orbit Challenge",
            "type": "challenge",
            "description": "Scouting for low-earth orbit satellite communication solutions and debris management.",
            "benefits": "$200k prize + orbital testing slot",
            "status": "published",
            "banner_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop"
        },
        {
            "title": "BioTech Health Accelerator",
            "type": "accelerator",
            "description": "A specialized program for drug discovery and genetic sequencing startups.",
            "benefits": "Wet lab access + $150k seed investment",
            "status": "published",
            "banner_url": "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?q=80&w=2070&auto=format&fit=crop"
        },
        {
            "title": "GovTech Digital Summit",
            "type": "pilot",
            "description": "Governments seeking digital identity and e-governance solutions for citizen services.",
            "benefits": "National scale implementation + long-term contract",
            "status": "published",
            "banner_url": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=2070&auto=format&fit=crop"
        }
    ]
    
    programs_added = 0
    for p in mock_programs:
        if not Opportunity.query.filter_by(title=p["title"]).first():
            new_opp = Opportunity(
                title=p["title"],
                type=p["type"],
                description=p["description"],
                benefits=p["benefits"],
                status=p["status"],
                banner_url=p.get('banner_url'),
                owner_id=current_user.id,
                deadline=datetime.utcnow() + timedelta(days=60),
                sectors='["fintech", "cleantech", "retail", "health"]',
                target_stages='["seed", "series_a"]',
                countries='["Global"]'
            )
            db.session.add(new_opp)
            programs_added += 1
    
    # 3. SEED SAMPLE MEETINGS
    from models import Meeting, MeetingParticipant
    import string
    import random
    
    def generate_meeting_room_id():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    sample_meetings = [
        {
            "title": "Weekly Startup Pitch Session",
            "description": "Present your startup to potential investors and get feedback",
            "scheduled_at": datetime.utcnow() + timedelta(days=2, hours=14),
            "duration_minutes": 90,
            "access_type": "startup_only"
        },
        {
            "title": "Corporate Innovation Roundtable",
            "description": "Discuss emerging technologies and partnership opportunities",
            "scheduled_at": datetime.utcnow() + timedelta(days=5, hours=10),
            "duration_minutes": 60,
            "access_type": "corporate_only"
        },
        {
            "title": "All Hands Platform Update",
            "description": "Monthly platform updates and community announcements",
            "scheduled_at": datetime.utcnow() + timedelta(days=7, hours=16),
            "duration_minutes": 45,
            "access_type": "all_users"
        }
    ]
    
    meetings_added = 0
    for m in sample_meetings:
        if not Meeting.query.filter_by(title=m["title"]).first():
            meeting_room_id = generate_meeting_room_id()
            while Meeting.query.filter_by(meeting_room_id=meeting_room_id).first():
                meeting_room_id = generate_meeting_room_id()
            
            new_meeting = Meeting(
                created_by_id=current_user.id,
                title=m["title"],
                description=m["description"],
                scheduled_at=m["scheduled_at"],
                duration_minutes=m["duration_minutes"],
                access_type=m["access_type"],
                meeting_room_id=meeting_room_id,
                meeting_password=''.join(random.choices(string.ascii_letters + string.digits, k=8)),
                meeting_url=f"/meeting/join/{meeting_room_id}"
            )
            db.session.add(new_meeting)
            db.session.flush()  # Get the meeting ID
            
            # Add participants based on access type
            if m["access_type"] == "all_users":
                users = User.query.filter_by(is_active=True).all()
            elif m["access_type"] == "startup_only":
                users = User.query.filter(User.role.in_(["startup", "founder"]), User.is_active == True).all()
            elif m["access_type"] == "corporate_only":
                users = User.query.filter_by(role="corporate", is_active=True).all()
            else:
                users = []
            
            for user in users:
                participant = MeetingParticipant(
                    meeting_id=new_meeting.id,
                    user_id=user.id,
                    is_moderator=(user.id == current_user.id)
                )
                db.session.add(participant)
            
            meetings_added += 1
    
    db.session.commit()
    return jsonify({
        "success": True, 
        "message": f"Successfully seeded {users_added} users, {programs_added} programs, and {meetings_added} meetings.",
        "users_added": users_added,
        "programs_added": programs_added,
        "meetings_added": meetings_added
    })


# ---------------------------------------
# UPDATE USER
# ---------------------------------------
@bp.route("/users/<int:id>", methods=["PUT"])
@login_required
def update_user(id):
# ... existing code ...

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


# ---------------------------------------
# UPLOAD POSTER (Admin Only)
# ---------------------------------------
@bp.route("/upload-poster", methods=["POST"])
@login_required
def upload_poster():
    if require_admin():
        return require_admin()

    if 'poster' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['poster']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Check file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        return jsonify({"error": "Invalid file type. Please upload PNG, JPG, JPEG, GIF, or WEBP files."}), 400

    # Check file size (max 5MB)
    if len(file.read()) > 5 * 1024 * 1024:
        return jsonify({"error": "File too large. Maximum size is 5MB."}), 400
    
    # Reset file pointer
    file.seek(0)

    try:
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'posters')
        os.makedirs(upload_dir, exist_ok=True)

        # Generate secure filename
        filename = secure_filename(file.filename)
        # Add timestamp to avoid conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)

        # Return the URL path
        poster_url = f"/static/uploads/posters/{filename}"
        
        return jsonify({
            "success": True,
            "poster_url": poster_url,
            "filename": filename
        })

    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500


# ---------------------------------------
# ANALYTICS ENDPOINTS
# ---------------------------------------

@bp.route("/analytics/user-growth", methods=["GET"])
@login_required
def analytics_user_growth():
    """Get user growth analytics"""
    if require_admin():
        return require_admin()
    
    days = request.args.get('days', 30, type=int)
    data = AdminAnalyticsService.get_user_growth_analytics(days)
    return jsonify({"success": True, "data": data})


@bp.route("/analytics/application-funnel", methods=["GET"])
@login_required
def analytics_application_funnel():
    """Get application funnel analytics"""
    if require_admin():
        return require_admin()
    
    data = AdminAnalyticsService.get_application_funnel()
    return jsonify({"success": True, "data": data})


@bp.route("/analytics/program-performance", methods=["GET"])
@login_required
def analytics_program_performance():
    """Get program performance analytics"""
    if require_admin():
        return require_admin()
    
    data = AdminAnalyticsService.get_program_performance()
    return jsonify({"success": True, "data": data})


@bp.route("/analytics/referrals", methods=["GET"])
@login_required
def analytics_referrals():
    """Get referral analytics"""
    if require_admin():
        return require_admin()
    
    data = AdminAnalyticsService.get_referral_analytics()
    return jsonify({"success": True, "data": data})


@bp.route("/analytics/meetings", methods=["GET"])
@login_required
def analytics_meetings():
    """Get meeting analytics"""
    if require_admin():
        return require_admin()
    
    days = request.args.get('days', 30, type=int)
    data = AdminAnalyticsService.get_meeting_analytics(days)
    return jsonify({"success": True, "data": data})


@bp.route("/analytics/leads", methods=["GET"])
@login_required
def analytics_leads():
    """Get lead analytics"""
    if require_admin():
        return require_admin()
    
    days = request.args.get('days', 30, type=int)
    data = AdminAnalyticsService.get_lead_analytics(days)
    return jsonify({"success": True, "data": data})


@bp.route("/analytics/platform-health", methods=["GET"])
@login_required
def analytics_platform_health():
    """Get platform health metrics"""
    if require_admin():
        return require_admin()
    
    data = AdminAnalyticsService.get_platform_health()
    return jsonify({"success": True, "data": data})


@bp.route("/analytics/revenue", methods=["GET"])
@login_required
def analytics_revenue():
    """Get revenue analytics"""
    if require_admin():
        return require_admin()
    
    days = request.args.get('days', 30, type=int)
    data = AdminAnalyticsService.get_revenue_analytics(days)
    return jsonify({"success": True, "data": data})


@bp.route("/analytics/comprehensive", methods=["GET"])
@login_required
def analytics_comprehensive():
    """Get comprehensive analytics report"""
    if require_admin():
        return require_admin()
    
    days = request.args.get('days', 30, type=int)
    data = AdminAnalyticsService.get_comprehensive_report(days)
    return jsonify({"success": True, "data": data})


@bp.route("/analytics/export/<analytics_type>", methods=["GET"])
@login_required
def analytics_export(analytics_type):
    """Export analytics data as CSV"""
    if require_admin():
        return require_admin()
    
    days = request.args.get('days', 30, type=int)
    
    try:
        csv_data = AdminAnalyticsService.export_analytics_csv(analytics_type, days)
        
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={analytics_type}_analytics.csv"}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# ---------------------------------------
# ADVANCED SEARCH ENDPOINTS
# ---------------------------------------

from admin_search_service import AdminSearchService

@bp.route("/search/users", methods=["GET"])
@login_required
def search_users():
    """Advanced user search with filters"""
    if require_admin():
        return require_admin()
    
    query = request.args.get('q')
    role = request.args.get('role')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    status = request.args.get('status')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Convert date strings to datetime
    if date_from:
        date_from = datetime.fromisoformat(date_from)
    if date_to:
        date_to = datetime.fromisoformat(date_to)
    
    results = AdminSearchService.search_users(
        query=query,
        role=role,
        date_from=date_from,
        date_to=date_to,
        status=status,
        limit=limit,
        offset=offset
    )
    
    return jsonify({"success": True, "data": results})


@bp.route("/search/programs", methods=["GET"])
@login_required
def search_programs():
    """Advanced program search with filters"""
    if require_admin():
        return require_admin()
    
    query = request.args.get('q')
    type = request.args.get('type')
    status = request.args.get('status')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    if date_from:
        date_from = datetime.fromisoformat(date_from)
    if date_to:
        date_to = datetime.fromisoformat(date_to)
    
    results = AdminSearchService.search_programs(
        query=query,
        type=type,
        status=status,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset
    )
    
    return jsonify({"success": True, "data": results})


@bp.route("/search/applications", methods=["GET"])
@login_required
def search_applications():
    """Advanced application search with filters"""
    if require_admin():
        return require_admin()
    
    query = request.args.get('q')
    status = request.args.get('status')
    program_id = request.args.get('program_id', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    if date_from:
        date_from = datetime.fromisoformat(date_from)
    if date_to:
        date_to = datetime.fromisoformat(date_to)
    
    results = AdminSearchService.search_applications(
        query=query,
        status=status,
        program_id=program_id,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset
    )
    
    return jsonify({"success": True, "data": results})


@bp.route("/search/meetings", methods=["GET"])
@login_required
def search_meetings():
    """Advanced meeting search with filters"""
    if require_admin():
        return require_admin()
    
    query = request.args.get('q')
    status = request.args.get('status')
    access_type = request.args.get('access_type')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    if date_from:
        date_from = datetime.fromisoformat(date_from)
    if date_to:
        date_to = datetime.fromisoformat(date_to)
    
    results = AdminSearchService.search_meetings(
        query=query,
        status=status,
        access_type=access_type,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset
    )
    
    return jsonify({"success": True, "data": results})


@bp.route("/search/referrals", methods=["GET"])
@login_required
def search_referrals():
    """Advanced referral search with filters"""
    if require_admin():
        return require_admin()
    
    query = request.args.get('q')
    status = request.args.get('status')
    enabler_id = request.args.get('enabler_id', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    if date_from:
        date_from = datetime.fromisoformat(date_from)
    if date_to:
        date_to = datetime.fromisoformat(date_to)
    
    results = AdminSearchService.search_referrals(
        query=query,
        status=status,
        enabler_id=enabler_id,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset
    )
    
    return jsonify({"success": True, "data": results})


@bp.route("/search/leads", methods=["GET"])
@login_required
def search_leads():
    """Advanced lead search with filters"""
    if require_admin():
        return require_admin()
    
    query = request.args.get('q')
    type = request.args.get('type')
    is_read = request.args.get('is_read')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Convert is_read to boolean
    if is_read is not None:
        is_read = is_read.lower() == 'true'
    
    if date_from:
        date_from = datetime.fromisoformat(date_from)
    if date_to:
        date_to = datetime.fromisoformat(date_to)
    
    results = AdminSearchService.search_leads(
        query=query,
        type=type,
        is_read=is_read,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset
    )
    
    return jsonify({"success": True, "data": results})


@bp.route("/search/global", methods=["GET"])
@login_required
def global_search():
    """Global search across all entities"""
    if require_admin():
        return require_admin()
    
    query = request.args.get('q')
    limit = request.args.get('limit', 20, type=int)
    
    if not query:
        return jsonify({"success": False, "error": "Query parameter required"}), 400
    
    results = AdminSearchService.global_search(query, limit)
    
    return jsonify({"success": True, "data": results})


@bp.route("/search/filter-options", methods=["GET"])
@login_required
def get_filter_options():
    """Get available filter options"""
    if require_admin():
        return require_admin()
    
    options = AdminSearchService.get_filter_options()
    
    return jsonify({"success": True, "data": options})


# ---------------------------------------
# BULK OPERATIONS ENDPOINTS
# ---------------------------------------

from admin_bulk_operations_service import AdminBulkOperationsService

@bp.route("/bulk/users/update", methods=["POST"])
@login_required
def bulk_update_users():
    """Bulk update users"""
    if require_admin():
        return require_admin()
    
    data = request.get_json()
    user_ids = data.get('user_ids', [])
    updates = data.get('updates', {})
    
    if not user_ids:
        return jsonify({"success": False, "error": "No user IDs provided"}), 400
    
    result = AdminBulkOperationsService.bulk_update_users(user_ids, updates)
    
    return jsonify(result)


@bp.route("/bulk/users/delete", methods=["POST"])
@login_required
def bulk_delete_users():
    """Bulk delete users"""
    if require_admin():
        return require_admin()
    
    data = request.get_json()
    user_ids = data.get('user_ids', [])
    confirm = data.get('confirm', False)
    
    if not user_ids:
        return jsonify({"success": False, "error": "No user IDs provided"}), 400
    
    result = AdminBulkOperationsService.bulk_delete_users(user_ids, confirm)
    
    return jsonify(result)


@bp.route("/bulk/users/export", methods=["POST"])
@login_required
def bulk_export_users():
    """Bulk export users"""
    if require_admin():
        return require_admin()
    
    data = request.get_json()
    user_ids = data.get('user_ids')
    format = data.get('format', 'csv')
    
    result = AdminBulkOperationsService.bulk_export_users(user_ids, format)
    
    if format == 'csv':
        return Response(
            result,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=users_export.csv"}
        )
    else:
        return jsonify(result)


@bp.route("/bulk/programs/update", methods=["POST"])
@login_required
def bulk_update_programs():
    """Bulk update programs"""
    if require_admin():
        return require_admin()
    
    data = request.get_json()
    program_ids = data.get('program_ids', [])
    updates = data.get('updates', {})
    
    if not program_ids:
        return jsonify({"success": False, "error": "No program IDs provided"}), 400
    
    result = AdminBulkOperationsService.bulk_update_programs(program_ids, updates)
    
    return jsonify(result)


@bp.route("/bulk/programs/delete", methods=["POST"])
@login_required
def bulk_delete_programs():
    """Bulk delete programs"""
    if require_admin():
        return require_admin()
    
    data = request.get_json()
    program_ids = data.get('program_ids', [])
    confirm = data.get('confirm', False)
    
    if not program_ids:
        return jsonify({"success": False, "error": "No program IDs provided"}), 400
    
    result = AdminBulkOperationsService.bulk_delete_programs(program_ids, confirm)
    
    return jsonify(result)


@bp.route("/bulk/applications/update-status", methods=["POST"])
@login_required
def bulk_update_application_status():
    """Bulk update application statuses"""
    if require_admin():
        return require_admin()
    
    data = request.get_json()
    application_ids = data.get('application_ids', [])
    status = data.get('status')
    note = data.get('note')
    
    if not application_ids:
        return jsonify({"success": False, "error": "No application IDs provided"}), 400
    
    if not status:
        return jsonify({"success": False, "error": "Status is required"}), 400
    
    result = AdminBulkOperationsService.bulk_update_application_status(application_ids, status, note)
    
    return jsonify(result)


@bp.route("/bulk/meetings/update-status", methods=["POST"])
@login_required
def bulk_update_meeting_status():
    """Bulk update meeting statuses"""
    if require_admin():
        return require_admin()
    
    data = request.get_json()
    meeting_ids = data.get('meeting_ids', [])
    status = data.get('status')
    
    if not meeting_ids:
        return jsonify({"success": False, "error": "No meeting IDs provided"}), 400
    
    if not status:
        return jsonify({"success": False, "error": "Status is required"}), 400
    
    result = AdminBulkOperationsService.bulk_update_meeting_status(meeting_ids, status)
    
    return jsonify(result)


@bp.route("/bulk/meetings/delete", methods=["POST"])
@login_required
def bulk_delete_meetings():
    """Bulk delete meetings"""
    if require_admin():
        return require_admin()
    
    data = request.get_json()
    meeting_ids = data.get('meeting_ids', [])
    confirm = data.get('confirm', False)
    
    if not meeting_ids:
        return jsonify({"success": False, "error": "No meeting IDs provided"}), 400
    
    result = AdminBulkOperationsService.bulk_delete_meetings(meeting_ids, confirm)
    
    return jsonify(result)


@bp.route("/bulk/leads/mark-read", methods=["POST"])
@login_required
def bulk_mark_leads_read():
    """Bulk mark leads as read"""
    if require_admin():
        return require_admin()
    
    data = request.get_json()
    lead_ids = data.get('lead_ids', [])
    
    if not lead_ids:
        return jsonify({"success": False, "error": "No lead IDs provided"}), 400
    
    result = AdminBulkOperationsService.bulk_mark_leads_read(lead_ids)
    
    return jsonify(result)


@bp.route("/bulk/leads/delete", methods=["POST"])
@login_required
def bulk_delete_leads():
    """Bulk delete leads"""
    if require_admin():
        return require_admin()
    
    data = request.get_json()
    lead_ids = data.get('lead_ids', [])
    confirm = data.get('confirm', False)
    
    if not lead_ids:
        return jsonify({"success": False, "error": "No lead IDs provided"}), 400
    
    result = AdminBulkOperationsService.bulk_delete_leads(lead_ids, confirm)
    
    return jsonify(result)


@bp.route("/bulk/referrals/update-status", methods=["POST"])
@login_required
def bulk_update_referral_status():
    """Bulk update referral statuses"""
    if require_admin():
        return require_admin()
    
    data = request.get_json()
    referral_ids = data.get('referral_ids', [])
    status = data.get('status')
    
    if not referral_ids:
        return jsonify({"success": False, "error": "No referral IDs provided"}), 400
    
    if not status:
        return jsonify({"success": False, "error": "Status is required"}), 400
    
    result = AdminBulkOperationsService.bulk_update_referral_status(referral_ids, status)
    
    return jsonify(result)


@bp.route("/bulk/summary", methods=["POST"])
@login_required
def get_bulk_operation_summary():
    """Get summary before bulk operation"""
    if require_admin():
        return require_admin()
    
    data = request.get_json()
    entity_type = data.get('entity_type')
    entity_ids = data.get('entity_ids', [])
    
    if not entity_type or not entity_ids:
        return jsonify({"success": False, "error": "Entity type and IDs required"}), 400
    
    summary = AdminBulkOperationsService.get_bulk_operation_summary(entity_type, entity_ids)
    
    return jsonify({"success": True, "summary": summary})
