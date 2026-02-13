# routes/enablers.py
from flask import Blueprint, jsonify, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Referral, Startup, Opportunity, User, Application
from extensions import db
from enabler_service import EnablerService

bp = Blueprint("enablers", __name__, url_prefix="/api/enabler")

# Web Blueprint for connector settings routes
connector_web_bp = Blueprint('connector_web', __name__, url_prefix='/connector')

@bp.route("/dashboard/overview", methods=["GET"])
@login_required
def get_overview():
    """Get enabler dashboard overview with real data"""
    if current_user.role not in ("enabler", "admin"):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    timeframe = request.args.get('timeframe', '30d')
    
    result = EnablerService.get_dashboard_overview(current_user.id, timeframe)
    return jsonify(result)

@bp.route("/rewards/summary", methods=["GET"])
@login_required
def get_rewards_summary():
    """Get rewards summary with real calculations"""
    if current_user.role not in ("enabler", "admin"):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    result = EnablerService.get_rewards_summary(current_user.id)
    return jsonify(result)

@bp.route("/rewards/history", methods=["GET"])
@login_required
def get_rewards_history():
    """Get rewards transaction history"""
    if current_user.role not in ("enabler", "admin"):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    r_type = request.args.get('type', 'all').lower()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    result = EnablerService.get_rewards_history(current_user.id, r_type, page, per_page)
    return jsonify(result)

@bp.route("/analytics", methods=["GET"])
@login_required
def get_analytics():
    """Get detailed analytics with real data"""
    if current_user.role not in ("enabler", "admin"):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    result = EnablerService.get_analytics(current_user.id)
    return jsonify(result)

@bp.route("/referrals", methods=["GET"])
@login_required
def get_referrals():
    """Get all referrals for enabler"""
    if current_user.role not in ("enabler", "admin"):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    status = request.args.get('status')
    limit = request.args.get('limit', type=int)
    
    result = EnablerService.get_enabler_referrals(current_user.id, status, limit)
    return jsonify(result)

@bp.route("/referrals/create", methods=["POST"])
@login_required
def create_referral():
    """Create a new referral"""
    if current_user.role not in ("enabler", "admin"):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    data = request.get_json()
    
    required_fields = ["opportunity_id", "startup_name", "startup_email"]
    if not all(field in data for field in required_fields):
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    result = EnablerService.create_referral(
        enabler_id=current_user.id,
        opportunity_id=data["opportunity_id"],
        startup_name=data["startup_name"],
        startup_email=data["startup_email"],
        notes=data.get("notes")
    )
    
    return jsonify(result)

@bp.route("/links/generate", methods=["POST"])
@login_required
def generate_link():
    """Generate a referral link"""
    if current_user.role not in ("enabler", "admin"):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    data = request.get_json()
    
    if "opportunity_id" not in data:
        return jsonify({"success": False, "message": "opportunity_id required"}), 400

    result = EnablerService.generate_referral_link(
        enabler_id=current_user.id,
        opportunity_id=data["opportunity_id"]
    )
    
    return jsonify(result)

@bp.route("/links/stats", methods=["GET"])
@login_required
def get_link_stats():
    """Get referral link tracking statistics"""
    if current_user.role not in ("enabler", "admin"):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    result = EnablerService.get_link_tracking_stats(current_user.id)
    return jsonify(result)

@bp.route("/level", methods=["GET"])
@login_required
def get_level():
    """Get enabler level and gamification stats"""
    if current_user.role not in ("enabler", "admin"):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    result = EnablerService.get_enabler_level(current_user.id)
    return jsonify(result)

@bp.route("/payout/request", methods=["POST"])
@login_required
def request_payout():
    """Request a payout"""
    if current_user.role not in ("enabler", "admin"):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    data = request.get_json()
    
    if "amount" not in data:
        return jsonify({"success": False, "message": "amount required"}), 400

    result = EnablerService.request_payout(
        enabler_id=current_user.id,
        amount=data["amount"],
        payout_method=data.get("payout_method", "bank_transfer")
    )
    
    return jsonify(result)


@bp.route("/settings/upload_photo", methods=["POST"])
@login_required
def upload_photo_api():
    """Upload profile photo via API"""
    try:
        if current_user.role not in ("enabler", "admin"):
            return jsonify({"success": False, "message": "Unauthorized"}), 403
        
        if 'profile_pic' not in request.files:
            return jsonify({"success": False, "message": "No file part"}), 400
        
        file = request.files['profile_pic']
        
        if file.filename == '':
            return jsonify({"success": False, "message": "No selected file"}), 400
        
        if file and file.filename.rsplit('.', 1)[1].lower() in ['jpg', 'jpeg', 'png', 'gif']:
            import os
            from werkzeug.utils import secure_filename
            
            filename = secure_filename(f"profile_{current_user.id}_{file.filename}")
            upload_folder = 'static/uploads/profiles'
            os.makedirs(upload_folder, exist_ok=True)
            
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            current_user.profile_pic = f"/{file_path}"
            db.session.commit()
            
            return jsonify({
                "success": True,
                "message": "Photo uploaded successfully",
                "profile_pic_url": f"/{file_path}"
            })
        else:
            return jsonify({"success": False, "message": "Invalid file type"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@connector_web_bp.route("/settings/remove_photo", methods=["POST"])
@login_required
def remove_profile_photo():
    """Remove user profile photo"""
    try:
        if current_user.role not in ("enabler", "admin"):
            return redirect(url_for('index'))
        
        if current_user.profile_pic:
            current_user.profile_pic = None
            db.session.commit()
            flash('Profile photo removed successfully.', 'success')
        else:
            flash('No profile photo to remove.', 'info')
        
        return redirect(url_for('enabler_page'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error removing photo: {str(e)}', 'error')
        return redirect(url_for('enabler_page'))


@connector_web_bp.route("/settings/upload_photo", methods=["POST"])
@login_required
def upload_photo():
    """Upload profile photo"""
    try:
        if current_user.role not in ("enabler", "admin"):
            return jsonify({"success": False, "message": "Unauthorized"}), 403
        
        if 'profile_pic' not in request.files:
            return jsonify({"success": False, "message": "No file part"}), 400
        
        file = request.files['profile_pic']
        
        if file.filename == '':
            return jsonify({"success": False, "message": "No selected file"}), 400
        
        if file and file.filename.rsplit('.', 1)[1].lower() in ['jpg', 'jpeg', 'png', 'gif']:
            import os
            from werkzeug.utils import secure_filename
            
            filename = secure_filename(f"profile_{current_user.id}_{file.filename}")
            upload_folder = 'static/uploads/profiles'
            os.makedirs(upload_folder, exist_ok=True)
            
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            current_user.profile_pic = f"/{file_path}"
            db.session.commit()
            
            return jsonify({
                "success": True,
                "message": "Photo uploaded successfully",
                "profile_pic_url": f"/{file_path}"
            })
        else:
            return jsonify({"success": False, "message": "Invalid file type"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
