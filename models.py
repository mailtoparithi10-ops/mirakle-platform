# models.py
from datetime import datetime
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import json


# -----------------------------------------
# USER MODEL (Founder, Connector, Corporate, Admin)
# -----------------------------------------
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(40), default="founder")  
    # founder, connector, corporate, admin

    country = db.Column(db.String(120))
    region = db.Column(db.String(120))
    company = db.Column(db.String(200))

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # RELATIONSHIPS
    startups = db.relationship("Startup", backref="founder", lazy=True)
    opportunities = db.relationship("Opportunity", backref="owner", lazy=True)

    # PASSWORD HELPERS
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # REQUIRED BY FLASK-LOGIN
    def get_id(self):
        return str(self.id)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "country": self.country,
            "region": self.region,
            "company": self.company,
        }


# -----------------------------------------
# STARTUP MODEL
# -----------------------------------------
class Startup(db.Model):
    __tablename__ = "startups"

    id = db.Column(db.Integer, primary_key=True)
    founder_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    name = db.Column(db.String(220), nullable=False)
    website = db.Column(db.String(400))

    country = db.Column(db.String(120))
    region = db.Column(db.String(120))

    sectors = db.Column(db.Text)  # JSON list
    stage = db.Column(db.String(120))
    team_size = db.Column(db.String(100))
    funding = db.Column(db.String(100))

    problem = db.Column(db.Text)
    solution = db.Column(db.Text)
    traction = db.Column(db.Text)

    pitch_deck_url = db.Column(db.String(500))
    demo_url = db.Column(db.String(500))

    tags = db.Column(db.Text)  # JSON list

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "founder_id": self.founder_id,
            "name": self.name,
            "website": self.website,
            "country": self.country,
            "region": self.region,
            "sectors": json.loads(self.sectors or "[]"),
            "stage": self.stage,
            "team_size": self.team_size,
            "funding": self.funding,
            "problem": self.problem,
            "solution": self.solution,
            "traction": self.traction,
            "pitch_deck_url": self.pitch_deck_url,
            "demo_url": self.demo_url,
            "tags": json.loads(self.tags or "[]"),
        }


# -----------------------------------------
# OPPORTUNITY MODEL
# -----------------------------------------
class Opportunity(db.Model):
    __tablename__ = "opportunities"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    title = db.Column(db.String(300), nullable=False)
    type = db.Column(db.String(120))  # accelerator, grant, PoC, etc.
    description = db.Column(db.Text)
    eligibility = db.Column(db.Text)

    sectors = db.Column(db.Text)  # JSON list
    target_stages = db.Column(db.Text)  # JSON list
    countries = db.Column(db.Text)  # JSON list

    deadline = db.Column(db.DateTime)
    benefits = db.Column(db.Text)

    status = db.Column(db.String(40), default="draft")  
    # draft, published, closed

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "title": self.title,
            "type": self.type,
            "description": self.description,
            "eligibility": self.eligibility,
            "sectors": json.loads(self.sectors or "[]"),
            "target_stages": json.loads(self.target_stages or "[]"),
            "countries": json.loads(self.countries or "[]"),
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "benefits": self.benefits,
            "status": self.status,
        }


# -----------------------------------------
# APPLICATION MODEL
# -----------------------------------------
class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)

    startup_id = db.Column(db.Integer, db.ForeignKey("startups.id"), nullable=False)
    opportunity_id = db.Column(db.Integer, db.ForeignKey("opportunities.id"), nullable=False)
    applied_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    status = db.Column(
        db.String(60), default="draft"
    )  
    # draft, submitted, under_review, shortlisted, rejected, selected

    timeline = db.Column(db.Text)  # JSON list
    notes = db.Column(db.Text)  # JSON list

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "startup_id": self.startup_id,
            "opportunity_id": self.opportunity_id,
            "applied_by_id": self.applied_by_id,
            "status": self.status,
            "timeline": json.loads(self.timeline or "[]"),
            "notes": json.loads(self.notes or "[]"),
            "created_at": self.created_at.isoformat(),
        }


# -----------------------------------------
# REFERRAL MODEL
# -----------------------------------------
class Referral(db.Model):
    __tablename__ = "referrals"

    id = db.Column(db.Integer, primary_key=True)

    connector_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    startup_id = db.Column(db.Integer, db.ForeignKey("startups.id"), nullable=False)
    opportunity_id = db.Column(db.Integer, db.ForeignKey("opportunities.id"), nullable=False)

    status = db.Column(db.String(40), default="open")  
    # open, successful, failed

    reward_log = db.Column(db.Text)  # JSON list

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "connector_id": self.connector_id,
            "startup_id": self.startup_id,
            "opportunity_id": self.opportunity_id,
            "status": self.status,
            "reward_log": json.loads(self.reward_log or "[]"),
            "created_at": self.created_at.isoformat(),
        }


# -----------------------------------------
# CONTACT MESSAGE MODEL
# -----------------------------------------
class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "subject": self.subject,
            "message": self.message,
            "created_at": self.created_at.isoformat(),
            "is_read": self.is_read
        }


# -----------------------------------------
# MEETING MODEL
# -----------------------------------------
class Meeting(db.Model):
    __tablename__ = "meetings"

    id = db.Column(db.Integer, primary_key=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    
    # Meeting scheduling
    scheduled_at = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    timezone = db.Column(db.String(50), default="UTC")
    
    # Meeting access control
    access_type = db.Column(db.String(50), nullable=False)  
    # 'all_users', 'startup_only', 'corporate_only', 'connector_only', 'specific_users'
    
    # Meeting features (Zoom-like capabilities)
    video_enabled = db.Column(db.Boolean, default=True)
    audio_enabled = db.Column(db.Boolean, default=True)
    screen_sharing_enabled = db.Column(db.Boolean, default=True)
    recording_enabled = db.Column(db.Boolean, default=False)
    chat_enabled = db.Column(db.Boolean, default=True)
    waiting_room_enabled = db.Column(db.Boolean, default=False)
    
    # Meeting room settings
    meeting_room_id = db.Column(db.String(100), unique=True, nullable=False)
    meeting_password = db.Column(db.String(50))
    max_participants = db.Column(db.Integer, default=100)
    
    # Status and metadata
    status = db.Column(db.String(50), default="scheduled")  
    # scheduled, in_progress, completed, cancelled
    
    meeting_url = db.Column(db.String(500))
    recording_url = db.Column(db.String(500))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_by = db.relationship("User", backref="created_meetings")
    participants = db.relationship("MeetingParticipant", backref="meeting", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "created_by_id": self.created_by_id,
            "created_by_name": self.created_by.name if self.created_by else None,
            "title": self.title,
            "description": self.description,
            "scheduled_at": self.scheduled_at.isoformat(),
            "duration_minutes": self.duration_minutes,
            "timezone": self.timezone,
            "access_type": self.access_type,
            "video_enabled": self.video_enabled,
            "audio_enabled": self.audio_enabled,
            "screen_sharing_enabled": self.screen_sharing_enabled,
            "recording_enabled": self.recording_enabled,
            "chat_enabled": self.chat_enabled,
            "waiting_room_enabled": self.waiting_room_enabled,
            "meeting_room_id": self.meeting_room_id,
            "meeting_password": self.meeting_password,
            "max_participants": self.max_participants,
            "status": self.status,
            "meeting_url": self.meeting_url,
            "recording_url": self.recording_url,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "participant_count": len(self.participants)
        }


# -----------------------------------------
# MEETING PARTICIPANT MODEL
# -----------------------------------------
class MeetingParticipant(db.Model):
    __tablename__ = "meeting_participants"

    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey("meetings.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # Null for external participants
    
    # For external participants (non-registered users)
    external_name = db.Column(db.String(100))
    external_email = db.Column(db.String(120))
    
    # Participant permissions
    can_share_screen = db.Column(db.Boolean, default=True)
    can_use_chat = db.Column(db.Boolean, default=True)
    is_moderator = db.Column(db.Boolean, default=False)
    
    # Participation tracking
    joined_at = db.Column(db.DateTime)
    left_at = db.Column(db.DateTime)
    attendance_status = db.Column(db.String(50), default="invited")  
    # invited, joined, left, no_show
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", backref="meeting_participations")
    
    def to_dict(self):
        return {
            "id": self.id,
            "meeting_id": self.meeting_id,
            "user_id": self.user_id,
            "user_name": self.user.name if self.user else self.external_name,
            "user_email": self.user.email if self.user else self.external_email,
            "user_role": self.user.role if self.user else "external",
            "external_name": self.external_name,
            "external_email": self.external_email,
            "can_share_screen": self.can_share_screen,
            "can_use_chat": self.can_use_chat,
            "is_moderator": self.is_moderator,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
            "left_at": self.left_at.isoformat() if self.left_at else None,
            "attendance_status": self.attendance_status,
            "created_at": self.created_at.isoformat()
        }
