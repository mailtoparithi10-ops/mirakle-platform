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
            "status": "published"
        },
        {
            "title": "Sustainability Innovation Grant",
            "type": "grant",
            "description": "Government-backed grant for startups working on carbon sequestration technologies.",
            "benefits": "Up to $100k non-dilutive funding",
            "status": "published"
        },
        {
            "title": "Retail Tech Pilot - MegaCorp",
            "type": "pilot",
            "description": "MegaCorp is scouting for AI solutions to optimize supply chain logistics for their retail outlets.",
            "benefits": "Paid PoC + distribution opportunity",
            "status": "published"
        },
        {
            "title": "HealthTech Challenge APAC",
            "type": "challenge",
            "description": "Solving regional healthcare accessibility through mobile-first digital solutions.",
            "benefits": "Pilot with regional hospital networks",
            "status": "published"
        },
        {
            "title": "DeepTech Pioneer Program",
            "type": "accelerator",
            "description": "Unlocking breakthroughs in quantum computing and material sciences.",
            "benefits": "Lab access + $100k investment",
            "status": "published"
        },
        {
            "title": "Web3 Innovation Grant",
            "type": "grant",
            "description": "Building the future of decentralized finance and identity on the blockchain.",
            "benefits": "$25k non-equity grant",
            "status": "published"
        },
        {
            "title": "AgriTech Smart Farming Initiative",
            "type": "pilot",
            "description": "Scouting for IoT and AI solutions to optimize crop yields and reduce waste in agriculture.",
            "benefits": "Implementation pilot + $40k funding",
            "status": "published"
        },
        {
            "title": "EdTech Catalyst Program",
            "type": "accelerator",
            "description": "Bridging the digital divide with innovative remote learning tools for rural schools.",
            "benefits": "Mentorship + $30h grant",
            "status": "published"
        },
        {
            "title": "ClimateTech Carbon Challenge",
            "type": "challenge",
            "description": "Scouting for high-impact carbon capture and sequestration technologies.",
            "benefits": "$500k prize pool + pilot opportunity",
            "status": "published"
        },
        {
            "title": "SpaceTech Orbit Challenge",
            "type": "challenge",
            "description": "Scouting for low-earth orbit satellite communication solutions and debris management.",
            "benefits": "$200k prize + orbital testing slot",
            "status": "published"
        },
        {
            "title": "BioTech Health Accelerator",
            "type": "accelerator",
            "description": "A specialized program for drug discovery and genetic sequencing startups.",
            "benefits": "Wet lab access + $150k seed investment",
            "status": "published"
        },
        {
            "title": "GovTech Digital Summit",
            "type": "pilot",
            "description": "Governments seeking digital identity and e-governance solutions for citizen services.",
            "benefits": "National scale implementation + long-term contract",
            "status": "published"
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
