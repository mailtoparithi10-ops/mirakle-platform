# routes/meetings.py
from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from extensions import db
from models import Meeting, MeetingParticipant, User, Notification
from datetime import datetime, timedelta
import uuid
import random
import string

bp = Blueprint("meetings", __name__, url_prefix="/api/meetings")

# Web routes for meeting pages
web_bp = Blueprint("meetings_web", __name__, url_prefix="/meetings")


def require_admin():
    """Helper function to check admin access"""
    if not current_user.is_authenticated or current_user.role != "admin":
        return jsonify({"error": "Admin access required"}), 403
    return None


def generate_meeting_room_id():
    """Generate unique meeting room ID"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


def generate_meeting_password():
    """Generate random meeting password"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


# -----------------------------------------
# WEB ROUTES
# -----------------------------------------
@web_bp.route('/')
@login_required
def meetings_view():
    """User-friendly meetings view for all users"""
    return render_template('meetings_user_view.html')


@web_bp.route('/join/<meeting_room_id>')
@login_required
def join_meeting_page(meeting_room_id):
    """Meeting join page"""
    meeting = Meeting.query.filter_by(meeting_room_id=meeting_room_id).first_or_404()
    
    # Check if user has access
    participant = MeetingParticipant.query.filter_by(
        meeting_id=meeting.id,
        user_id=current_user.id
    ).first()
    
    # If not a participant, check if user is admin
    if not participant and current_user.role == "admin":
        participant = MeetingParticipant(
            meeting_id=meeting.id,
            user_id=current_user.id,
            is_moderator=True
        )
        db.session.add(participant)
        try:
            db.session.commit()
        except Exception as e:
            print(f"Error adding admin as participant: {e}")
            db.session.rollback()
    
    if not participant:
        return render_template('403.html'), 403
    
    return render_template('meeting_join.html', meeting=meeting)


def create_meeting_notification(meeting_id, notification_type, custom_message=None):
    """Create notifications for meeting participants"""
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return False
    
    participants = MeetingParticipant.query.filter_by(meeting_id=meeting_id).all()
    
    templates = {
        'created': {
            'title': f'New Meeting: {meeting.title}',
            'message': f'You have been invited to "{meeting.title}" scheduled for {meeting.scheduled_at.strftime("%B %d, %Y at %I:%M %p")}.',
            'type': 'info'
        },
        'updated': {
            'title': f'Meeting Updated: {meeting.title}',
            'message': f'The meeting "{meeting.title}" has been updated. Please check the details.',
            'type': 'warning'
        },
        'reminder': {
            'title': f'Meeting Reminder: {meeting.title}',
            'message': f'Your meeting "{meeting.title}" starts in 15 minutes. Click to join.',
            'type': 'info'
        },
        'cancelled': {
            'title': f'Meeting Cancelled: {meeting.title}',
            'message': f'The meeting "{meeting.title}" has been cancelled.',
            'type': 'danger'
        }
    }
    
    template = templates.get(notification_type, templates['created'])
    if custom_message:
        template['message'] = custom_message
    
    notifications_created = 0
    for participant in participants:
        if participant.user_id:
            notification = Notification(
                user_id=participant.user_id,
                title=template['title'],
                message=template['message'],
                type=template['type'],
                link=f'/meetings/join/{meeting.meeting_room_id}'
            )
            db.session.add(notification)
            notifications_created += 1
    
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return False


# -----------------------------------------
# CREATE MEETING (Admin Only)
# -----------------------------------------
@bp.route("/create", methods=["POST"])
@login_required
def create_meeting():
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ["title", "scheduled_at", "access_type"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    try:
        # Parse scheduled time
        scheduled_at = datetime.fromisoformat(data["scheduled_at"].replace('Z', '+00:00'))
        
        # Generate unique meeting identifiers
        meeting_room_id = generate_meeting_room_id()
        while Meeting.query.filter_by(meeting_room_id=meeting_room_id).first():
            meeting_room_id = generate_meeting_room_id()
        
        # Create meeting
        meeting = Meeting(
            created_by_id=current_user.id,
            title=data["title"],
            description=data.get("description", ""),
            scheduled_at=scheduled_at,
            duration_minutes=data.get("duration_minutes", 60),
            timezone=data.get("timezone", "UTC"),
            access_type=data["access_type"],
            video_enabled=data.get("video_enabled", True),
            audio_enabled=data.get("audio_enabled", True),
            screen_sharing_enabled=data.get("screen_sharing_enabled", True),
            recording_enabled=data.get("recording_enabled", False),
            chat_enabled=data.get("chat_enabled", True),
            waiting_room_enabled=data.get("waiting_room_enabled", False),
            meeting_room_id=meeting_room_id,
            meeting_password=generate_meeting_password(),
            max_participants=data.get("max_participants", 100),
            meeting_url=f"/meeting/join/{meeting_room_id}"
        )
        
        db.session.add(meeting)
        db.session.flush()  # Get the meeting ID
        
        # Add participants based on access type
        if data["access_type"] == "all_users":
            users = User.query.filter_by(is_active=True).all()
            for user in users:
                participant = MeetingParticipant(
                    meeting_id=meeting.id,
                    user_id=user.id,
                    is_moderator=(user.id == current_user.id or user.role == "admin")
                )
                db.session.add(participant)
        
        elif data["access_type"] in ["startup_only", "corporate_only", "connector_only"]:
            role_mapping = {
                "startup_only": ["startup", "founder"],
                "corporate_only": ["corporate"],
                "connector_only": ["connector", "enabler"]
            }
            roles = role_mapping[data["access_type"]]
            users = User.query.filter(User.role.in_(roles), User.is_active == True).all()
            
            # Always include admin users in any meeting
            admin_users = User.query.filter_by(role="admin", is_active=True).all()
            all_users = list(users) + [admin for admin in admin_users if admin not in users]
            
            for user in all_users:
                participant = MeetingParticipant(
                    meeting_id=meeting.id,
                    user_id=user.id,
                    is_moderator=(user.id == current_user.id or user.role == "admin")
                )
                db.session.add(participant)
        
        elif data["access_type"] == "specific_users":
            user_ids = data.get("specific_user_ids", [])
            
            # Always include admin users in specific meetings
            admin_users = User.query.filter_by(role="admin", is_active=True).all()
            admin_ids = [admin.id for admin in admin_users]
            all_user_ids = list(set(user_ids + admin_ids))  # Remove duplicates
            
            for user_id in all_user_ids:
                user = User.query.get(user_id)
                if user and user.is_active:
                    participant = MeetingParticipant(
                        meeting_id=meeting.id,
                        user_id=user.id,
                        is_moderator=(user.id == current_user.id or user.role == "admin")
                    )
                    db.session.add(participant)
        
        # Add external participants if provided
        external_participants = data.get("external_participants", [])
        for ext_participant in external_participants:
            participant = MeetingParticipant(
                meeting_id=meeting.id,
                external_name=ext_participant.get("name"),
                external_email=ext_participant.get("email")
            )
            db.session.add(participant)
        
        db.session.commit()
        
        # Create notifications for participants
        create_meeting_notification(meeting.id, 'created')
        
        return jsonify({
            "success": True,
            "message": "Meeting created successfully",
            "meeting": meeting.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create meeting: {str(e)}"}), 500


# -----------------------------------------
# GET ALL MEETINGS (Admin)
# -----------------------------------------
@bp.route("/", methods=["GET"])
@login_required
def get_meetings():
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    meetings = Meeting.query.order_by(Meeting.scheduled_at.desc()).all()
    return jsonify({
        "success": True,
        "meetings": [meeting.to_dict() for meeting in meetings]
    })


# -----------------------------------------
# GET USER'S MEETINGS (For Dashboard Inbox)
# -----------------------------------------
@bp.route("/my-meetings", methods=["GET"])
@login_required
def get_user_meetings():
    try:
        print(f"DEBUG: get_user_meetings called by user {current_user.id} ({current_user.email})")
        
        # Get meetings where user is a participant
        participant_meetings = db.session.query(Meeting).join(MeetingParticipant).filter(
            MeetingParticipant.user_id == current_user.id
        ).order_by(Meeting.scheduled_at.asc()).all()
        
        print(f"DEBUG: Found {len(participant_meetings)} meetings for user")
        
        # Separate upcoming and past meetings
        now = datetime.utcnow()
        upcoming_meetings = [m for m in participant_meetings if m.scheduled_at > now]
        past_meetings = [m for m in participant_meetings if m.scheduled_at <= now]
        
        print(f"DEBUG: {len(upcoming_meetings)} upcoming, {len(past_meetings)} past")
        
        response_data = {
            "success": True,
            "upcoming_meetings": [meeting.to_dict() for meeting in upcoming_meetings],
            "past_meetings": [meeting.to_dict() for meeting in past_meetings]
        }
        
        print(f"DEBUG: Returning response with {len(response_data['upcoming_meetings'])} upcoming meetings")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"ERROR in get_user_meetings: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# -----------------------------------------
# GET MEETING DETAILS
# -----------------------------------------
@bp.route("/<int:meeting_id>", methods=["GET"])
@login_required
def get_meeting(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    
    # Check if user has access to this meeting
    if current_user.role != "admin":
        participant = MeetingParticipant.query.filter_by(
            meeting_id=meeting_id,
            user_id=current_user.id
        ).first()
        
        if not participant:
            return jsonify({"error": "Access denied"}), 403
    
    return jsonify({
        "success": True,
        "meeting": meeting.to_dict(),
        "participants": [p.to_dict() for p in meeting.participants]
    })


# -----------------------------------------
# UPDATE MEETING (Admin Only)
# -----------------------------------------
@bp.route("/<int:meeting_id>", methods=["PUT"])
@login_required
def update_meeting(meeting_id):
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    meeting = Meeting.query.get_or_404(meeting_id)
    data = request.get_json()
    
    try:
        # Update meeting fields
        if "title" in data:
            meeting.title = data["title"]
        if "description" in data:
            meeting.description = data["description"]
        if "scheduled_at" in data:
            meeting.scheduled_at = datetime.fromisoformat(data["scheduled_at"].replace('Z', '+00:00'))
        if "duration_minutes" in data:
            meeting.duration_minutes = data["duration_minutes"]
        if "status" in data:
            meeting.status = data["status"]
        
        # Update meeting features
        feature_fields = [
            "video_enabled", "audio_enabled", "screen_sharing_enabled",
            "recording_enabled", "chat_enabled", "waiting_room_enabled"
        ]
        for field in feature_fields:
            if field in data:
                setattr(meeting, field, data[field])
        
        meeting.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Create update notification
        create_meeting_notification(meeting_id, 'updated')
        
        return jsonify({
            "success": True,
            "message": "Meeting updated successfully",
            "meeting": meeting.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update meeting: {str(e)}"}), 500


# -----------------------------------------
# DELETE MEETING (Admin Only)
# -----------------------------------------
@bp.route("/<int:meeting_id>", methods=["DELETE"])
@login_required
def delete_meeting(meeting_id):
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    meeting = Meeting.query.get_or_404(meeting_id)
    
    try:
        # Create cancellation notification before deleting
        create_meeting_notification(meeting_id, 'cancelled')
        
        db.session.delete(meeting)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Meeting deleted successfully"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete meeting: {str(e)}"}), 500


# -----------------------------------------
# JOIN MEETING
# -----------------------------------------
@bp.route("/join/<meeting_room_id>", methods=["GET", "POST"])
@login_required
def join_meeting(meeting_room_id):
    meeting = Meeting.query.filter_by(meeting_room_id=meeting_room_id).first_or_404()
    
    # Check if user has access
    participant = MeetingParticipant.query.filter_by(
        meeting_id=meeting.id,
        user_id=current_user.id
    ).first()
    
    # If not a participant, check if user is admin (admins can join any meeting)
    if not participant and current_user.role == "admin":
        # Create participant entry for admin user
        participant = MeetingParticipant(
            meeting_id=meeting.id,
            user_id=current_user.id,
            is_moderator=True  # Admins are always moderators
        )
        db.session.add(participant)
        try:
            db.session.commit()
        except Exception as e:
            print(f"Error adding admin as participant: {e}")
            db.session.rollback()
    
    if not participant:
        return jsonify({"error": "Access denied to this meeting"}), 403
    
    # Update participant status
    if request.method == "POST":
        participant.joined_at = datetime.utcnow()
        participant.attendance_status = "joined"
        db.session.commit()
    
    return jsonify({
        "success": True,
        "meeting": meeting.to_dict(),
        "participant": participant.to_dict(),
        "join_url": f"/meeting/room/{meeting_room_id}"
    })


# -----------------------------------------
# LEAVE MEETING
# -----------------------------------------
@bp.route("/leave/<meeting_room_id>", methods=["POST"])
@login_required
def leave_meeting(meeting_room_id):
    meeting = Meeting.query.filter_by(meeting_room_id=meeting_room_id).first_or_404()
    
    participant = MeetingParticipant.query.filter_by(
        meeting_id=meeting.id,
        user_id=current_user.id
    ).first()
    
    if participant:
        participant.left_at = datetime.utcnow()
        participant.attendance_status = "left"
        db.session.commit()
    
    return jsonify({
        "success": True,
        "message": "Left meeting successfully"
    })


# -----------------------------------------
# GET MEETING STATISTICS (Admin)
# -----------------------------------------
@bp.route("/stats", methods=["GET"])
@login_required
def get_meeting_stats():
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    total_meetings = Meeting.query.count()
    upcoming_meetings = Meeting.query.filter(Meeting.scheduled_at > datetime.utcnow()).count()
    completed_meetings = Meeting.query.filter_by(status="completed").count()
    
    # Participation stats
    total_participants = MeetingParticipant.query.count()
    active_participants = MeetingParticipant.query.filter_by(attendance_status="joined").count()
    
    return jsonify({
        "success": True,
        "stats": {
            "total_meetings": total_meetings,
            "upcoming_meetings": upcoming_meetings,
            "completed_meetings": completed_meetings,
            "total_participants": total_participants,
            "active_participants": active_participants
        }
    })