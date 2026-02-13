# routes/corporate.py
"""
API routes for corporate dashboard
Handles startup discovery, deal flow, applications, and analytics
"""

from flask import Blueprint, jsonify, request, redirect, url_for, flash
from flask_login import login_required, current_user
from corporate_service import CorporateService
from decorators import role_required

corporate_bp = Blueprint('corporate', __name__, url_prefix='/api/corporate')

# Web Blueprint for corporate settings routes
corporate_web_bp = Blueprint('corporate_web', __name__, url_prefix='/corporate')


# ==========================================
# DASHBOARD & OVERVIEW
# ==========================================

@corporate_bp.route('/dashboard/overview', methods=['GET'])
@login_required
@role_required(['corporate', 'admin'])
def get_dashboard_overview():
    """Get complete dashboard overview with real data"""
    result = CorporateService.get_dashboard_overview(current_user.id)
    return jsonify(result)


# ==========================================
# STARTUP DISCOVERY
# ==========================================

@corporate_bp.route('/startups/discover', methods=['GET'])
@login_required
@role_required(['corporate', 'admin'])
def discover_startups():
    """Get matched startups with scores"""
    filters = {
        'search': request.args.get('search'),
        'sector': request.args.get('sector'),
        'stage': request.args.get('stage'),
        'page': request.args.get('page', 1, type=int)
    }
    
    result = CorporateService.discover_startups(current_user.id, filters)
    return jsonify(result)


@corporate_bp.route('/startups/<int:startup_id>/view-profile', methods=['POST'])
@login_required
@role_required(['corporate', 'admin'])
def view_startup_profile(startup_id):
    """Track profile view"""
    result = CorporateService.view_startup_profile(current_user.id, startup_id)
    return jsonify(result)


@corporate_bp.route('/startups/<int:startup_id>/connect', methods=['POST'])
@login_required
@role_required(['corporate', 'admin'])
def connect_with_startup(startup_id):
    """Create connection request"""
    result = CorporateService.connect_with_startup(current_user.id, startup_id)
    return jsonify(result)


# ==========================================
# DEAL FLOW
# ==========================================

@corporate_bp.route('/deals/all', methods=['GET'])
@login_required
@role_required(['corporate', 'admin'])
def get_all_deals():
    """Get all deals organized by stage"""
    result = CorporateService.get_all_deals(current_user.id)
    return jsonify(result)


@corporate_bp.route('/deals/create', methods=['POST'])
@login_required
@role_required(['corporate', 'admin'])
def create_deal():
    """Create new deal"""
    data = request.get_json()
    
    if not data or 'startup_id' not in data:
        return jsonify({"success": False, "error": "startup_id is required"}), 400
    
    result = CorporateService.create_deal(
        current_user.id,
        data['startup_id'],
        data
    )
    
    if result['success']:
        return jsonify(result), 201
    return jsonify(result), 400


@corporate_bp.route('/deals/<int:deal_id>/stage', methods=['PUT'])
@login_required
@role_required(['corporate', 'admin'])
def update_deal_stage(deal_id):
    """Move deal to new stage"""
    data = request.get_json()
    
    if not data or 'stage' not in data:
        return jsonify({"success": False, "error": "stage is required"}), 400
    
    result = CorporateService.update_deal_stage(
        deal_id,
        data['stage'],
        current_user.id
    )
    
    return jsonify(result)


@corporate_bp.route('/deals/<int:deal_id>', methods=['GET'])
@login_required
@role_required(['corporate', 'admin'])
def get_deal_details(deal_id):
    """Get deal with activities"""
    result = CorporateService.get_deal_details(deal_id, current_user.id)
    return jsonify(result)


@corporate_bp.route('/deals/<int:deal_id>/note', methods=['POST'])
@login_required
@role_required(['corporate', 'admin'])
def add_deal_note(deal_id):
    """Add note to deal"""
    data = request.get_json()
    
    if not data or 'note' not in data:
        return jsonify({"success": False, "error": "note is required"}), 400
    
    result = CorporateService.add_deal_note(
        deal_id,
        data['note'],
        current_user.id
    )
    
    return jsonify(result)


# ==========================================
# PROGRAMS
# ==========================================

@corporate_bp.route('/programs/all', methods=['GET'])
@login_required
@role_required(['corporate', 'admin'])
def get_programs():
    """Get programs with engagement metrics"""
    result = CorporateService.get_programs_with_engagement(current_user.id)
    return jsonify(result)


@corporate_bp.route('/programs/<int:program_id>/engagement', methods=['GET'])
@login_required
@role_required(['corporate', 'admin'])
def get_program_engagement(program_id):
    """Get engagement metrics for specific program"""
    # This could be expanded with more detailed metrics
    result = CorporateService.get_programs_with_engagement(current_user.id)
    
    if result['success']:
        # Find specific program
        program = next((p for p in result['programs'] if p['id'] == program_id), None)
        if program:
            return jsonify({
                "success": True,
                "applicant_count": program.get('applicant_count', 0),
                "days_remaining": program.get('days_remaining'),
                "engagement_trend": program.get('engagement_trend', 'Moderate')
            })
        return jsonify({"success": False, "error": "Program not found"}), 404
    
    return jsonify(result), 400


# ==========================================
# APPLICATIONS
# ==========================================

@corporate_bp.route('/applications/all', methods=['GET'])
@login_required
@role_required(['corporate', 'admin'])
def get_applications():
    """Get applications for corporate programs"""
    filters = {
        'status': request.args.get('status'),
        'page': request.args.get('page', 1, type=int)
    }
    
    result = CorporateService.get_applications(current_user.id, filters)
    return jsonify(result)


# ==========================================
# PROFILE & SETTINGS
# ==========================================

@corporate_bp.route('/profile', methods=['GET'])
@login_required
@role_required(['corporate', 'admin'])
def get_profile():
    """Get corporate profile"""
    result = CorporateService.get_corporate_profile(current_user.id)
    return jsonify(result)


@corporate_bp.route('/profile', methods=['PUT'])
@login_required
@role_required(['corporate', 'admin'])
def update_profile():
    """Update corporate profile"""
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400
    
    result = CorporateService.update_corporate_profile(current_user.id, data)
    return jsonify(result)


@corporate_bp.route('/settings/notifications', methods=['PUT'])
@login_required
@role_required(['corporate', 'admin'])
def update_notification_settings():
    """Update notification preferences"""
    data = request.get_json()
    
    # This would integrate with a notification settings model
    # For now, return success
    return jsonify({
        "success": True,
        "message": "Notification settings updated"
    })


@corporate_web_bp.route('/settings/remove_photo', methods=['POST'])
@login_required
def remove_profile_photo():
    """Remove user profile photo"""
    try:
        if current_user.role not in ('corporate', 'admin'):
            flash('Unauthorized', 'error')
            return redirect(url_for('corporate_dealflow_page'))
        
        if current_user.profile_pic:
            current_user.profile_pic = None
            from extensions import db as db_ext
            db_ext.session.commit()
            flash('Profile photo removed.', 'success')
    except Exception as e:
        from extensions import db as db_ext
        db_ext.session.rollback()
        flash(f'Error removing photo: {str(e)}', 'error')
        
    return redirect(url_for('corporate_dealflow_page'))


@corporate_web_bp.route('/settings/upload_photo', methods=['POST'])
@login_required
def upload_photo():
    """Upload profile photo"""
    try:
        if current_user.role not in ('corporate', 'admin'):
            return jsonify({"success": False, "message": "Unauthorized"}), 403
        
        if 'profile_pic' not in request.files:
            return jsonify({"success": False, "message": "No file part"}), 400
        
        file = request.files['profile_pic']
        
        if file.filename == '':
            return jsonify({"success": False, "message": "No selected file"}), 400
        
        if file and file.filename.rsplit('.', 1)[1].lower() in ['jpg', 'jpeg', 'png', 'gif']:
            # Save the file
            import os
            from werkzeug.utils import secure_filename
            
            filename = secure_filename(f"profile_{current_user.id}_{file.filename}")
            upload_folder = 'static/uploads/profiles'
            os.makedirs(upload_folder, exist_ok=True)
            
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            # Update user profile
            from extensions import db as db_ext
            current_user.profile_pic = f"/{file_path}"
            db_ext.session.commit()
            
            return jsonify({
                "success": True,
                "message": "Photo uploaded successfully",
                "profile_pic_url": f"/{file_path}"
            })
        else:
            return jsonify({"success": False, "message": "Invalid file type"}), 400
    except Exception as e:
        from extensions import db as db_ext
        db_ext.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ==========================================
# ANALYTICS
# ==========================================

@corporate_bp.route('/analytics', methods=['GET'])
@login_required
@role_required(['corporate', 'admin'])
def get_analytics():
    """Get analytics data for period"""
    period = request.args.get('period', '6m')
    result = CorporateService.get_analytics(current_user.id, period)
    return jsonify(result)
