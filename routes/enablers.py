# routes/enablers.py
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import Referral, Startup, Opportunity, User
from extensions import db
import random

bp = Blueprint("enablers", __name__, url_prefix="/api/enabler")

@bp.route("/dashboard/overview", methods=["GET"])
@login_required
def get_overview():
    if current_user.role not in ("connector", "enabler", "admin"):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    timeframe = request.args.get('timeframe', '30d')
    page = int(request.args.get('page', 1))
    
    # Calculate real stats
    referrals = Referral.query.filter_by(connector_id=current_user.id).order_by(Referral.created_at.desc()).all()
    total_referrals = len(referrals)
    
    # Mocking conversion and earnings for now based on referral count
    confirmed_earnings = total_referrals * 2500 
    flc_points = total_referrals * 120
    
    referral_list = []
    for r in referrals[:5]: # Last 5
        opp = Opportunity.query.get(r.opportunity_id)
        
        # Cross-reference with Applications
        app_status = None
        if r.startup_id:
            app = Application.query.filter_by(startup_id=r.startup_id, opportunity_id=r.opportunity_id).first()
            if app:
                app_status = app.status

        referral_list.append({
            "startup_name": r.startup_name,
            "program_name": opp.title if opp else "Unknown Program",
            "status": "successful" if r.status == 'accepted' else ("failed" if r.status == 'rejected' else "open"),
            "application_status": app_status,
            "created_at": r.created_at.isoformat(),
            "reward": "₹2,500"
        })

    return jsonify({
        "success": True,
        "data": {
            "summary": {
                "total_referrals": total_referrals,
                "confirmed_earnings": confirmed_earnings,
                "flc_points": flc_points,
                "conversion_rate": 0.32 if total_referrals > 0 else 0
            },
            "recent_referrals": referral_list
        }
    })

@bp.route("/rewards/summary", methods=["GET"])
@login_required
def get_rewards_summary():
    if current_user.role not in ("connector", "enabler", "admin"):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    return jsonify({
        "success": True,
        "data": {
            "available_balance": 32600,
            "pending_rewards": 18800,
            "all_time_earnings": 124200,
            "total_points": 3420,
            "average_reward_per_completed_referral": 4000
        }
    })

@bp.route("/rewards/history", methods=["GET"])
@login_required
def get_rewards_history():
    if current_user.role not in ("connector", "enabler", "admin"):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    r_type = request.args.get('type', 'all').lower()
    page = int(request.args.get('page', 1))
    
    if page == 1:
        all_items = [
            {"created_at": "2026-03-14", "startup_name": "FarmLink Labs", "program_name": "Retail Innovation Sprint", "reward_type": "cash", "amount_money": 8500, "status": "Settled", "payout_method": "Wallet"},
            {"created_at": "2026-03-05", "startup_name": "InnoBridge", "program_name": "Monthly Bonus", "reward_type": "points", "amount_points": 400, "status": "Posted", "payout_method": "Points"},
            {"created_at": "2026-02-12", "startup_name": "-", "program_name": "-", "reward_type": "payout", "amount_money": -15000, "status": "Completed", "payout_method": "Bank Transfer"},
            {"created_at": "2026-01-28", "startup_name": "NovaGrid Analytics", "program_name": "Smart City Innovation", "reward_type": "cash", "amount_money": 12000, "status": "Settled", "payout_method": "Wallet"},
            {"created_at": "2026-01-15", "startup_name": "MedSync Health", "program_name": "Health Pilot", "reward_type": "cash", "amount_money": 15000, "status": "Settled", "payout_method": "Wallet"}
        ]
    else:
        all_items = [
            {"created_at": "2025-12-20", "startup_name": "EcoFlow", "program_name": "Sustainability Grant", "reward_type": "cash", "amount_money": 5000, "status": "Settled", "payout_method": "Wallet"},
            {"created_at": "2025-11-15", "startup_name": "CyberShield", "program_name": "Cybersecurity Cohort", "reward_type": "cash", "amount_money": 10000, "status": "Settled", "payout_method": "Bank"},
            {"created_at": "2025-10-05", "startup_name": "InnoBridge", "program_name": "Q3 Top Connector", "reward_type": "points", "amount_points": 1200, "status": "Posted", "payout_method": "Points"},
            {"created_at": "2025-09-12", "startup_name": "UrbanLift", "program_name": "Mobility Program", "reward_type": "cash", "amount_money": 4500, "status": "Settled", "payout_method": "Wallet"}
        ]

    filtered_items = all_items
    if r_type != 'all':
        if r_type == 'bonuses':
             filtered_items = [i for i in all_items if 'bonus' in i['program_name'].lower()]
        else:
             filtered_items = [i for i in all_items if i['reward_type'] == r_type]

    return jsonify({
        "success": True,
        "data": {
            "items": filtered_items,
            "pagination": {
                "page": page,
                "total_pages": 4
            }
        }
    })

@bp.route("/analytics", methods=["GET"])
@login_required
def get_analytics():
    if current_user.role not in ("connector", "enabler", "admin"):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    return jsonify({
        "success": True,
        "data": {
            "referral_stats": {
                "submitted": 28,
                "shortlisted": 14,
                "completed": 9,
                "conversion": 32,
                "avg_programs_per_startup": 1.3,
                "avg_decision_time": 21
            },
            "sectors": [
                {"name": "HealthTech", "conversion": 48},
                {"name": "FinTech", "conversion": 36},
                {"name": "AgriTech", "conversion": 25}
            ],
            "signals": {
                "emerging": "Climate & sustainability programs",
                "best_days": "Tue–Thu",
                "best_time": "10am–1pm IST"
            }
        }
    })
