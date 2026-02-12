# routes/startups.py
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Startup
from werkzeug.utils import secure_filename
import json
import os
from datetime import datetime

bp = Blueprint('startups', __name__, url_prefix='/api/startups')

# Web routes for application form
web_bp = Blueprint('startup_web', __name__, url_prefix='/startup')

@web_bp.route('/apply')
@login_required
def application_form():
    """Display the startup application form"""
    if current_user.role not in ('founder', 'startup', 'admin'):
        flash('Only startup founders can access this page.', 'error')
        return redirect('/')
    
    # Get the program they're applying to (if any)
    program_id = request.args.get('program_id')
    program = None
    if program_id:
        from models import Opportunity
        program = Opportunity.query.get(program_id)
    
    # Check if user already has a startup application
    existing_startup = Startup.query.filter_by(founder_id=current_user.id).first()
    if existing_startup:
        # If they have a startup and are applying to a program, redirect to program application
        if program_id:
            flash('Redirecting to program application...', 'info')
            return redirect(f'/startup/apply/program/{program_id}')
        else:
            flash('You already have a startup application. You can edit it from your dashboard.', 'info')
            return redirect(url_for('startup_web.dashboard'))
    
    return render_template('startup_application.html', program=program)

@web_bp.route('/apply/program/<int:program_id>', methods=['GET', 'POST'])
@login_required
def apply_to_program(program_id):
    """Apply to a specific program - requires existing startup profile"""
    if current_user.role not in ('founder', 'startup', 'admin'):
        flash('Only startup founders can access this page.', 'error')
        return redirect('/')
    
    from models import Opportunity
    program = Opportunity.query.get_or_404(program_id)
    
    # Check if user has a startup profile
    startup = Startup.query.filter_by(founder_id=current_user.id).first()
    if not startup:
        flash('Please complete your startup profile first before applying to programs.', 'info')
        return redirect(url_for('startup_web.application_form', program_id=program_id))
    
    # Check if already applied
    from models import Application
    existing_app = Application.query.filter_by(
        startup_id=startup.id,
        opportunity_id=program_id
    ).first()
    
    if existing_app:
        flash('You have already applied to this program.', 'warning')
        return redirect(url_for('startup_web.dashboard'))
    
    # Handle Form Submission
    if request.method == 'POST':
        try:
            import json
            from datetime import datetime
            
            # 1. Update Startup Profile
            # Get form data
            startup.name = request.form.get('startup_name')
            startup.description = request.form.get('description')
            startup.location = request.form.get('location')
            startup.website = request.form.get('website')
            startup.linkedin = request.form.get('linkedin') # Note: model has distinct 'linkedin' field
            
            startup.stage = request.form.get('stage')
            startup.team_size = request.form.get('team_size')
            
            startup.business_model = request.form.get('business_model')
            startup.team_info = request.form.get('team_info')
            startup.financials = request.form.get('financials')

            # Parse sectors
            sectors = request.form.getlist('sectors')
            if sectors:
                startup.sectors = json.dumps(sectors)
                # primitive mapping for industry string if needed, although model uses sectors JSON usually
                startup.industry = ','.join(sectors) 

            # Parse founding date
            founding_date_str = request.form.get('founding_date')
            if founding_date_str:
                try:
                    startup.founding_date = datetime.strptime(founding_date_str, '%Y-%m-%d').date()
                except ValueError:
                    pass # Keep existing if invalid or handle error

            # Handle File Uploads (Logo & Pitch Deck)
            upload_dir = os.path.join('static', 'uploads', 'startups')
            os.makedirs(upload_dir, exist_ok=True)
            
            if 'logo' in request.files:
                logo_file = request.files['logo']
                if logo_file and logo_file.filename:
                    filename = secure_filename(f"{current_user.id}_{startup.name}_logo_{logo_file.filename}")
                    logo_path = os.path.join(upload_dir, filename)
                    logo_file.save(logo_path)
                    startup.logo_url = f"/static/uploads/startups/{filename}"

            if 'pitch_deck' in request.files:
                pitch_file = request.files['pitch_deck']
                if pitch_file and pitch_file.filename:
                    filename = secure_filename(f"{current_user.id}_{startup.name}_pitch_{pitch_file.filename}")
                    pitch_path = os.path.join(upload_dir, filename)
                    pitch_file.save(pitch_path)
                    startup.pitch_deck_url = f"/static/uploads/startups/{filename}"
            
            # Commit Profile Updates
            db.session.commit()

            # 2. Create Application
            timeline = [{
                "status": "submitted",
                "note": "Application submitted via portal",
                "at": datetime.utcnow().isoformat(),
                "by": current_user.id
            }]
            
            application = Application(
                startup_id=startup.id,
                opportunity_id=program_id,
                applied_by_id=current_user.id,
                status="submitted",
                timeline=json.dumps(timeline),
                notes=json.dumps({}) 
            )
            
            db.session.add(application)
            
            # Create notifications for program owner and administrators
            try:
                from models import Notification, User
                
                # 1. Notify the Opportunity Owner (e.g., Corporate User)
                if program.owner_id:
                    notif = Notification(
                        user_id=program.owner_id,
                        title="New Application Received",
                        message=f"Startup {startup.name} has applied to your program: {program.title}",
                        type="success",
                        link=f"/corporate#applications"
                    )
                    db.session.add(notif)
                
                # 2. Notify all Administrators
                admins = User.query.filter_by(role="admin").all()
                for admin in admins:
                    # Skip if admin is also the owner to avoid double notification
                    if program.owner_id and admin.id == program.owner_id:
                        continue
                        
                    admin_notif = Notification(
                        user_id=admin.id,
                        title="Program Application Alert",
                        message=f"New application from {startup.name} for {program.title}",
                        type="info",
                        link=f"/admin#programs"
                    )
                    db.session.add(admin_notif)
                    
            except Exception as e:
                print(f"Notification error: {e}")
            
            db.session.commit()
            
            flash(f'Successfully applied to {program.title}!', 'success')
            return redirect(url_for('startup_web.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting application: {str(e)}', 'error')
            return render_template('program_application.html', program=program, startup=startup)

    # Render Form
    return render_template('program_application.html', program=program, startup=startup)

@web_bp.route('/apply', methods=['POST'])
@login_required
def submit_application():
    """Handle startup application form submission"""
    if current_user.role not in ('founder', 'startup', 'admin'):
        return jsonify({'error': 'forbidden'}), 403
    
    # Check if user already has a startup
    existing_startup = Startup.query.filter_by(founder_id=current_user.id).first()
    if existing_startup:
        flash('You already have a startup application.', 'error')
        return redirect(url_for('startup_web.dashboard'))
    
    try:
        # Get form data
        startup_name = request.form.get('startup_name')
        description = request.form.get('description')
        location = request.form.get('location')
        website = request.form.get('website')
        linkedin = request.form.get('linkedin')
        stage = request.form.get('stage')
        founding_date_str = request.form.get('founding_date')
        team_size = request.form.get('team_size')
        business_model = request.form.get('business_model')
        team_info = request.form.get('team_info')
        financials = request.form.get('financials')
        
        # Get sectors (multiple checkboxes)
        sectors = request.form.getlist('sectors')
        
        # Validate required fields
        if not all([startup_name, description, location, stage, founding_date_str, team_size]):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('startup_web.application_form'))
        
        if not sectors:
            flash('Please select at least one sector.', 'error')
            return redirect(url_for('startup_web.application_form'))
        
        # Parse founding date
        founding_date = None
        if founding_date_str:
            try:
                founding_date = datetime.strptime(founding_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid founding date format.', 'error')
                return redirect(url_for('startup_web.application_form'))
        
        # Handle file uploads
        logo_url = None
        pitch_deck_url = None
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join('static', 'uploads', 'startups')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Handle logo upload
        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file and logo_file.filename:
                filename = secure_filename(f"{current_user.id}_{startup_name}_logo_{logo_file.filename}")
                logo_path = os.path.join(upload_dir, filename)
                logo_file.save(logo_path)
                logo_url = f"/static/uploads/startups/{filename}"
        
        # Handle pitch deck upload
        if 'pitch_deck' in request.files:
            pitch_file = request.files['pitch_deck']
            if pitch_file and pitch_file.filename:
                filename = secure_filename(f"{current_user.id}_{startup_name}_pitch_{pitch_file.filename}")
                pitch_path = os.path.join(upload_dir, filename)
                pitch_file.save(pitch_path)
                pitch_deck_url = f"/static/uploads/startups/{filename}"
        
        # Create startup record
        startup = Startup(
            founder_id=current_user.id,
            name=startup_name,
            description=description,
            location=location,
            website=website,
            linkedin=linkedin,
            sectors=json.dumps(sectors),
            stage=stage,
            founding_date=founding_date,
            team_size=team_size,
            business_model=business_model,
            team_info=team_info,
            financials=financials,
            logo_url=logo_url,
            pitch_deck_url=pitch_deck_url,
            application_status='submitted'
        )
        
        db.session.add(startup)
        db.session.commit()
        
        flash('Your startup application has been submitted successfully!', 'success')
        
        # Check if they were applying to a specific program
        program_id = request.form.get('program_id')
        if program_id:
            # Redirect to program application
            return redirect(f'/startup/apply/program/{program_id}')
        else:
            return redirect(url_for('startup_web.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while submitting your application: {str(e)}', 'error')
        return redirect(url_for('startup_web.application_form'))

@web_bp.route('/dashboard')
@login_required
def dashboard():
    """Startup dashboard"""
    if current_user.role not in ('founder', 'startup', 'admin'):
        flash('Access denied.', 'error')
        return redirect('/')
    
    startup = Startup.query.filter_by(founder_id=current_user.id).first()
    
    # If no startup application exists, redirect to application form
    if not startup:
        flash('Please complete your startup application to access the dashboard.', 'info')
        return redirect(url_for('startup_web.application_form'))
    
    # Check if startup profile is incomplete
    incomplete_profile = False
    missing_fields = []
    
    required_fields = {
        'description': 'Company description',
        'location': 'Company location',
        'stage': 'Startup stage'
    }
    
    for field, label in required_fields.items():
        if not getattr(startup, field):
            missing_fields.append(label)
            incomplete_profile = True
    
    if incomplete_profile:
        flash(f'Your profile is incomplete. Missing: {", ".join(missing_fields)}. Please update your profile.', 'warning')
    
    # Fetch Applications
    from models import Application, Referral, Opportunity, User
    raw_applications = Application.query.filter_by(startup_id=startup.id).order_by(Application.created_at.desc()).all()
    
    applications = []
    for app in raw_applications:
        opp = Opportunity.query.get(app.opportunity_id)
        applications.append({
            'title': opp.title if opp else 'Unknown Program',
            'created_at': app.created_at.strftime('%b %d, %Y'),
            'status': app.status,
            'last_update': 'Recently', # Placeholder logic for converting timeline timestamp
            'id': app.id
        })
    
    # Fetch Referrals
    raw_referrals = Referral.query.filter_by(startup_id=startup.id).order_by(Referral.created_at.desc()).all()
    referrals = []
    for ref in raw_referrals:
        enabler = User.query.get(ref.enabler_id)
        opp = Opportunity.query.get(ref.opportunity_id)
        referrals.append({
            'enabler_name': enabler.name if enabler else 'Unknown Enabler',
            'enabler_role': 'Enabler', # Could be enabler.company or dynamic
            'program_name': opp.title if opp else 'General Referral',
            'priority': 'High', # Placeholder
            'status': ref.status,
            'id': ref.id,
            'opportunity_id': ref.opportunity_id
        })
    
    # Fetch Stats
    stats = {
        'market_readiness': 'A.84', 
        'network_reach': len(raw_referrals) * 150 + 50, 
        'success_rate': '88%', 
        'hub_level': 'Lvl 4'
    }
    
    # Recent Milestones
    milestones = []
    for app in raw_applications[:3]:
        opp = Opportunity.query.get(app.opportunity_id)
        milestones.append({
            'icon': 'fas fa-rocket',
            'title': f'Applied to {opp.title if opp else "Program"}',
            'time': app.created_at.strftime('%b %d'),
            'type': 'application'
        })
    
    for ref in raw_referrals[:3]:
        milestones.append({
            'icon': 'fas fa-handshake',
            'title': f'Referral received', 
            'time': ref.created_at.strftime('%b %d'),
            'type': 'referral'
        })
    
    # Fetch Available Programs (Opportunities)
    all_programs = Opportunity.query.filter_by(status='open').order_by(Opportunity.created_at.desc()).limit(10).all()
    applied_opp_ids = [app.opportunity_id for app in raw_applications]
    available_programs = [p for p in all_programs if p.id not in applied_opp_ids]

    # Fetch Network Connections (Suggested)
    suggested_connections = User.query.filter(User.role.in_(['enabler', 'corporate'])).filter(User.id != current_user.id).limit(4).all()

    return render_template('startup_dashboard.html', 
                           startup=startup, 
                           incomplete_profile=incomplete_profile, 
                           missing_fields=missing_fields,
                           applications=applications,
                           referrals=referrals,
                           stats=stats,
                           milestones=milestones,
                           available_programs=available_programs,
                           suggested_connections=suggested_connections)

@web_bp.route('/profile/edit')
@login_required
def edit_profile():
    """Edit startup profile"""
    if current_user.role not in ('founder', 'startup', 'admin'):
        flash('Access denied.', 'error')
        return redirect('/')
    
    startup = Startup.query.filter_by(founder_id=current_user.id).first()
    if not startup:
        flash('Please complete your startup application first.', 'info')
        return redirect(url_for('startup_web.application_form'))
    
    return render_template('startup_application.html', startup=startup, edit_mode=True)

@web_bp.route('/profile/edit', methods=['POST'])
@login_required
def update_profile():
    """Update startup profile"""
    if current_user.role not in ('founder', 'startup', 'admin'):
        return jsonify({'error': 'forbidden'}), 403
    
    startup = Startup.query.filter_by(founder_id=current_user.id).first()
    if not startup:
        flash('Startup profile not found.', 'error')
        return redirect(url_for('startup_web.application_form'))
    
    try:
        # Update startup fields
        startup.name = request.form.get('startup_name', startup.name)
        startup.description = request.form.get('description', startup.description)
        startup.location = request.form.get('location', startup.location)
        startup.website = request.form.get('website', startup.website)
        startup.linkedin = request.form.get('linkedin', startup.linkedin)
        startup.stage = request.form.get('stage', startup.stage)
        startup.team_size = request.form.get('team_size', startup.team_size)
        startup.business_model = request.form.get('business_model', startup.business_model)
        startup.team_info = request.form.get('team_info', startup.team_info)
        startup.financials = request.form.get('financials', startup.financials)
        
        # Update sectors
        sectors = request.form.getlist('sectors')
        if sectors:
            startup.sectors = json.dumps(sectors)
        
        # Update founding date
        founding_date_str = request.form.get('founding_date')
        if founding_date_str:
            try:
                startup.founding_date = datetime.strptime(founding_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Handle file uploads if provided
        upload_dir = os.path.join('static', 'uploads', 'startups')
        os.makedirs(upload_dir, exist_ok=True)
        
        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file and logo_file.filename:
                filename = secure_filename(f"{current_user.id}_{startup.name}_logo_{logo_file.filename}")
                logo_path = os.path.join(upload_dir, filename)
                logo_file.save(logo_path)
                startup.logo_url = f"/static/uploads/startups/{filename}"
        
        if 'pitch_deck' in request.files:
            pitch_file = request.files['pitch_deck']
            if pitch_file and pitch_file.filename:
                filename = secure_filename(f"{current_user.id}_{startup.name}_pitch_{pitch_file.filename}")
                pitch_path = os.path.join(upload_dir, filename)
                pitch_file.save(pitch_path)
                startup.pitch_deck_url = f"/static/uploads/startups/{filename}"
        
        # Update status if it was draft
        if startup.application_status == 'draft':
            startup.application_status = 'submitted'
        
        db.session.commit()
        
        flash('Your startup profile has been updated successfully!', 'success')
        return redirect(url_for('startup_web.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating profile: {str(e)}', 'error')
        return redirect(url_for('startup_web.edit_profile'))

@web_bp.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    """Update user settings (profile pic, personal info, password)"""
    try:
        # Update Personal Info
        if 'full_name' in request.form:
            current_user.name = request.form['full_name']
        
        if 'email' in request.form:
             # Ideally initiate email change verification, but for now just update if needed or disable
             pass 
        
        if 'phone' in request.form:
             # Store in extra field if User model doesn't have it, or just ignore for now
             pass
        
        if 'location' in request.form:
             # Store in user.country or region? User model has country/region.
             # We might need to split or just store in region
             current_user.region = request.form['location']

        # Handle Profile Pic Upload
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename:
                upload_dir = os.path.join('static', 'uploads', 'users')
                os.makedirs(upload_dir, exist_ok=True)
                
                filename = secure_filename(f"user_{current_user.id}_{int(datetime.utcnow().timestamp())}_{file.filename}")
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                
                current_user.profile_pic = f"/static/uploads/users/{filename}"

        # Handle Password Change
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        current_password = request.form.get('current_password')
        
        if new_password and confirm_password:
             if new_password == confirm_password:
                 # If user has password (not google), verify current
                 if current_user.password_hash and current_password:
                     if current_user.check_password(current_password):
                         current_user.set_password(new_password)
                         flash('Password updated successfully.', 'success')
                     else:
                         flash('Incorrect current password.', 'error')
                 elif not current_user.password_hash:
                     # Setting password for the first time (e.g. Google user adding password)
                     current_user.set_password(new_password)
                     flash('Password set successfully.', 'success')
             else:
                 flash('New passwords do not match.', 'error')

        db.session.commit()
        flash('Account settings updated.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating settings: {str(e)}', 'error')
        
    return redirect(url_for('startup_web.dashboard'))

@web_bp.route('/settings/remove_photo', methods=['POST'])
@login_required
def remove_profile_photo():
    """Remove user profile photo"""
    try:
        if current_user.profile_pic:
            # Optional: delete the file from filesystem if you want to clean up
            # import os
            # if os.path.exists(current_user.profile_pic.lstrip('/')):
            #     os.remove(current_user.profile_pic.lstrip('/'))
            
            current_user.profile_pic = None
            db.session.commit()
            flash('Profile photo removed.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error removing photo: {str(e)}', 'error')
        
    return redirect(url_for('startup_web.dashboard'))

@web_bp.route('/applications/<int:application_id>')
@login_required
def view_application(application_id):
    from models import Application, Opportunity
    
    application = Application.query.get_or_404(application_id)
    
    # Check ownership
    startup = Startup.query.filter_by(founder_id=current_user.id).first()
    if not startup or application.startup_id != startup.id:
        flash('Access denied.', 'error')
        return redirect(url_for('startup_web.dashboard'))
        
    opportunity = Opportunity.query.get(application.opportunity_id)
    
    return render_template('application_details.html', application=application, opportunity=opportunity, startup=startup)

@bp.route('/', methods=['POST'])
@login_required
def create_startup():
    # Only founders (or admin) can create startups
    if current_user.role not in ('founder', 'startup', 'admin'):
        return jsonify({'error': 'forbidden'}), 403

    data = request.json or request.form or {}
    # required: name
    name = data.get('name')
    if not name:
        return jsonify({'error': 'name required'}), 400

    s = Startup(
        founder_id=current_user.id,
        name=name,
        website=data.get('website'),
        country=data.get('country'),
        region=data.get('region'),
        sectors=json.dumps(data.get('sectors', [])),
        stage=data.get('stage'),
        team_size=data.get('team_size'),
        funding=data.get('funding'),
        problem=data.get('problem'),
        solution=data.get('solution'),
        traction=data.get('traction'),
        pitch_deck_url=data.get('pitch_deck_url'),
        demo_url=data.get('demo_url'),
        tags=json.dumps(data.get('tags', []))
    )
    db.session.add(s)
    db.session.commit()
    return jsonify(s.to_dict()), 201

@bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_startup(id):
    s = Startup.query.get_or_404(id)
    # only founder owner or admin
    if current_user.id != s.founder_id and current_user.role != 'admin':
        return jsonify({'error': 'forbidden'}), 403

    data = request.json or request.form or {}
    for key in ['name','website','country','region','stage','team_size','funding','problem','solution','traction','pitch_deck_url','demo_url']:
        if key in data:
            setattr(s, key, data[key])
    if 'sectors' in data:
        s.sectors = json.dumps(data['sectors'])
    if 'tags' in data:
        s.tags = json.dumps(data['tags'])
    db.session.commit()
    return jsonify(s.to_dict())

@bp.route('/<int:id>', methods=['GET'])
def get_startup(id):
    s = Startup.query.get_or_404(id)
    return jsonify(s.to_dict())

@bp.route('/', methods=['GET'])
def list_startups():
    q = Startup.query
    country = request.args.get('country')
    sector = request.args.get('sector')
    stage = request.args.get('stage')
    founder = request.args.get('founder')
    if country:
        q = q.filter_by(country=country)
    if stage:
        q = q.filter_by(stage=stage)
    if founder:
        try:
            f_id = int(founder)
            q = q.filter_by(founder_id=f_id)
        except:
            pass
    if sector:
        q = q.filter(Startup.sectors.like(f'%{sector}%'))
    start = int(request.args.get('start', 0))
    limit = int(request.args.get('limit', 50))
    items = q.offset(start).limit(limit).all()
    return jsonify([i.to_dict() for i in items])

@bp.route('/mine', methods=['GET'])
@login_required
def list_my_startups():
    if current_user.role not in ('founder', 'startup', 'admin'):
        return jsonify({'error': 'forbidden'}), 403
    
    startups = Startup.query.filter_by(founder_id=current_user.id).all()
    return jsonify({
        "success": True,
        "startups": [s.to_dict() for s in startups]
    })

@bp.route('/analytics', methods=['GET'])
@login_required
def get_analytics():
    """Get real analytics data for the dashboard charts using AnalyticsService"""
    from analytics_service import AnalyticsService
    
    startup = Startup.query.filter_by(founder_id=current_user.id).first()
    if not startup:
        return jsonify({'error': 'Startup profile not found'}), 404

    # Use the analytics service to get real data
    analytics_data = AnalyticsService.get_startup_analytics(startup.id, days=180)
    
    if not analytics_data:
        return jsonify({'error': 'Failed to fetch analytics'}), 500
    
    return jsonify(analytics_data)

