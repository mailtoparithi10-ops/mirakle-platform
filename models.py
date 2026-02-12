# models.py
from datetime import datetime
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import json


# -----------------------------------------
# USER MODEL (Founder, Enabler, Corporate, Admin)
# -----------------------------------------
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for Google users
    google_id = db.Column(db.String(100), unique=True, nullable=True)  # Google OAuth ID
    profile_pic = db.Column(db.String(500), nullable=True)  # Profile Picture URL
    phone = db.Column(db.String(20), nullable=True)  # Phone number

    role = db.Column(db.String(40), default="founder")  
    # founder, enabler, corporate, admin

    country = db.Column(db.String(120))
    region = db.Column(db.String(120))
    company = db.Column(db.String(200))

    # Bank account details for enabler payouts
    bank_account_name = db.Column(db.String(200), nullable=True)
    bank_account_number = db.Column(db.String(50), nullable=True)
    bank_ifsc = db.Column(db.String(20), nullable=True)
    bank_name = db.Column(db.String(100), nullable=True)
    
    # Razorpay integration
    razorpay_contact_id = db.Column(db.String(100), nullable=True)
    razorpay_fund_account_id = db.Column(db.String(100), nullable=True)

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # RELATIONSHIPS
    startups = db.relationship("Startup", backref="founder", lazy=True)
    opportunities = db.relationship("Opportunity", backref="owner", lazy=True)

    # PASSWORD HELPERS
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:  # Google users don't have passwords
            return False
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
            "profile_pic": self.profile_pic,
            "phone": self.phone,
            "country": self.country,
            "region": self.region,
            "company": self.company,
            "bank_configured": bool(self.bank_account_number and self.bank_ifsc),
            "created_at": self.created_at.isoformat() if self.created_at else None
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
    linkedin = db.Column(db.String(400))

    country = db.Column(db.String(120))
    region = db.Column(db.String(120))
    location = db.Column(db.String(200))  # Headquarters location

    sectors = db.Column(db.Text)  # JSON list
    stage = db.Column(db.String(120))
    team_size = db.Column(db.String(100))
    funding = db.Column(db.String(100))
    founding_date = db.Column(db.Date)

    description = db.Column(db.Text)  # Short description (200 words)
    problem = db.Column(db.Text)
    solution = db.Column(db.Text)
    traction = db.Column(db.Text)
    business_model = db.Column(db.Text)
    team_info = db.Column(db.Text)
    financials = db.Column(db.Text)

    pitch_deck_url = db.Column(db.String(500))
    demo_url = db.Column(db.String(500))
    logo_url = db.Column(db.String(500))

    tags = db.Column(db.Text)  # JSON list

    # Application status
    application_status = db.Column(db.String(50), default="draft")  # draft, submitted, approved, rejected

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
            "linkedin": self.linkedin,
            "country": self.country,
            "region": self.region,
            "location": self.location,
            "sectors": json.loads(self.sectors or "[]"),
            "stage": self.stage,
            "team_size": self.team_size,
            "funding": self.funding,
            "founding_date": self.founding_date.isoformat() if self.founding_date else None,
            "description": self.description,
            "problem": self.problem,
            "solution": self.solution,
            "traction": self.traction,
            "business_model": self.business_model,
            "team_info": self.team_info,
            "financials": self.financials,
            "pitch_deck_url": self.pitch_deck_url,
            "demo_url": self.demo_url,
            "logo_url": self.logo_url,
            "tags": json.loads(self.tags or "[]"),
            "application_status": self.application_status,
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
    banner_url = db.Column(db.String(500))  # URL to program image

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
            "banner_url": self.banner_url,
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

    enabler_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    startup_id = db.Column(db.Integer, db.ForeignKey("startups.id"), nullable=True) # Can be null if startup user not yet matched
    opportunity_id = db.Column(db.Integer, db.ForeignKey("opportunities.id"), nullable=False)

    startup_name = db.Column(db.String(200))
    startup_email = db.Column(db.String(200))
    
    token = db.Column(db.String(100), unique=True)
    is_link_referral = db.Column(db.Boolean, default=False)
    
    status = db.Column(db.String(40), default="pending")  
    # pending (wait for startup), accepted (confirmed by startup), rejected, successful (rewarded), failed (not selected)

    reward_log = db.Column(db.Text)  # JSON list
    notes = db.Column(db.Text) # Enabler notes

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "token": self.token,
            "enabler_id": self.enabler_id,
            "startup_id": self.startup_id,
            "opportunity_id": self.opportunity_id,
            "startup_name": self.startup_name,
            "startup_email": self.startup_email,
            "status": self.status,
            "reward_log": json.loads(self.reward_log or "[]"),
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
        }


# -----------------------------------------
# REFERRAL LINK CLICK TRACKING MODEL
# -----------------------------------------
class ReferralClick(db.Model):
    __tablename__ = "referral_clicks"

    id = db.Column(db.Integer, primary_key=True)
    referral_id = db.Column(db.Integer, db.ForeignKey("referrals.id"), nullable=False)
    
    # User who clicked (if logged in)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    startup_id = db.Column(db.Integer, db.ForeignKey("startups.id"), nullable=True)
    
    # Tracking data
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Conversion tracking
    viewed_opportunity = db.Column(db.Boolean, default=False)
    applied = db.Column(db.Boolean, default=False)
    applied_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            "id": self.id,
            "referral_id": self.referral_id,
            "user_id": self.user_id,
            "startup_id": self.startup_id,
            "clicked_at": self.clicked_at.isoformat(),
            "viewed_opportunity": self.viewed_opportunity,
            "applied": self.applied,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None
        }


# -----------------------------------------
# LEAD / INQUIRY MODEL
# -----------------------------------------
class Lead(db.Model):
    __tablename__ = "leads"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False) # 'contact', 'demo', 'investor'
    
    name = db.Column(db.String(140), nullable=False)
    email = db.Column(db.String(180), nullable=False)
    company = db.Column(db.String(200))
    subject = db.Column(db.String(200))
    message = db.Column(db.Text)
    
    # JSON field for extra data (like 'interest' for demo)
    extra_data = db.Column(db.Text) 
    
    status = db.Column(db.String(50), default="new") # 'new', 'contacted', 'resolved'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "email": self.email,
            "company": self.company,
            "subject": self.subject,
            "message": self.message,
            "extra_data": json.loads(self.extra_data or "{}"),
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "is_read": self.is_read
        }

# -----------------------------------------
# CONTACT MESSAGE MODEL (Keeping for compatibility)
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
    # 'all_users', 'startup_only', 'corporate_only', 'enabler_only', 'specific_users'
    
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


# -----------------------------------------
# NOTIFICATION MODEL
# -----------------------------------------
class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default="info") # info, success, warning, danger
    link = db.Column(db.String(500))
    
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="notifications")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "message": self.message,
            "type": self.type,
            "link": self.link,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat()
        }


# -----------------------------------------
# ANALYTICS TRACKING MODEL
# -----------------------------------------
class AnalyticsEvent(db.Model):
    __tablename__ = "analytics_events"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    startup_id = db.Column(db.Integer, db.ForeignKey("startups.id"), nullable=True)
    
    event_type = db.Column(db.String(100), nullable=False)
    # profile_view, profile_update, application_filed, application_status_change,
    # referral_received, document_uploaded, document_viewed, connection_made,
    # message_sent, achievement_earned, login, logout
    
    event_data = db.Column(db.Text)  # JSON data specific to event
    event_metadata = db.Column(db.Text)  # Additional metadata (IP, user agent, etc.)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "startup_id": self.startup_id,
            "event_type": self.event_type,
            "event_data": json.loads(self.event_data or "{}"),
            "event_metadata": json.loads(self.event_metadata or "{}"),
            "created_at": self.created_at.isoformat()
        }


# -----------------------------------------
# STARTUP METRICS SNAPSHOT MODEL (Daily/Weekly aggregates)
# -----------------------------------------
class StartupMetrics(db.Model):
    __tablename__ = "startup_metrics"

    id = db.Column(db.Integer, primary_key=True)
    startup_id = db.Column(db.Integer, db.ForeignKey("startups.id"), nullable=False)
    
    # Snapshot date
    snapshot_date = db.Column(db.Date, nullable=False, index=True)
    
    # Funnel metrics
    profile_views = db.Column(db.Integer, default=0)
    referrals_received = db.Column(db.Integer, default=0)
    applications_filed = db.Column(db.Integer, default=0)
    applications_selected = db.Column(db.Integer, default=0)
    
    # Engagement metrics
    document_downloads = db.Column(db.Integer, default=0)
    connections_made = db.Column(db.Integer, default=0)
    messages_sent = db.Column(db.Integer, default=0)
    messages_received = db.Column(db.Integer, default=0)
    
    # Growth score (calculated)
    growth_score = db.Column(db.Integer, default=60)
    
    # Ecosystem fit scores
    tech_score = db.Column(db.Integer, default=70)
    market_score = db.Column(db.Integer, default=65)
    team_score = db.Column(db.Integer, default=60)
    capital_score = db.Column(db.Integer, default=60)
    product_score = db.Column(db.Integer, default=70)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    startup = db.relationship("Startup", backref="metrics_snapshots")

    def to_dict(self):
        return {
            "id": self.id,
            "startup_id": self.startup_id,
            "snapshot_date": self.snapshot_date.isoformat(),
            "profile_views": self.profile_views,
            "referrals_received": self.referrals_received,
            "applications_filed": self.applications_filed,
            "applications_selected": self.applications_selected,
            "document_downloads": self.document_downloads,
            "connections_made": self.connections_made,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "growth_score": self.growth_score,
            "tech_score": self.tech_score,
            "market_score": self.market_score,
            "team_score": self.team_score,
            "capital_score": self.capital_score,
            "product_score": self.product_score
        }


# -----------------------------------------
# MESSAGE MODEL
# -----------------------------------------
class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    subject = db.Column(db.String(300))
    body = db.Column(db.Text, nullable=False)
    
    # Message type for categorization
    message_type = db.Column(db.String(50), default="direct")  # direct, system, reward, referral
    
    # Context linking
    referral_id = db.Column(db.Integer, db.ForeignKey("referrals.id"), nullable=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey("opportunities.id"), nullable=True)
    
    # Thread support
    thread_id = db.Column(db.String(100), index=True)  # Group messages in conversation
    parent_message_id = db.Column(db.Integer, db.ForeignKey("messages.id"), nullable=True)
    
    # Attachments
    attachments = db.Column(db.Text)  # JSON list of file URLs
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    is_deleted_by_sender = db.Column(db.Boolean, default=False)
    is_deleted_by_recipient = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    sender = db.relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    recipient = db.relationship("User", foreign_keys=[recipient_id], backref="received_messages")
    replies = db.relationship("Message", backref=db.backref("parent", remote_side=[id]))

    def to_dict(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "sender_name": self.sender.name if self.sender else None,
            "sender_profile_pic": self.sender.profile_pic if self.sender else None,
            "sender_role": self.sender.role if self.sender else None,
            "recipient_id": self.recipient_id,
            "recipient_name": self.recipient.name if self.recipient else None,
            "subject": self.subject,
            "body": self.body,
            "message_type": self.message_type,
            "referral_id": self.referral_id,
            "opportunity_id": self.opportunity_id,
            "thread_id": self.thread_id,
            "parent_message_id": self.parent_message_id,
            "attachments": json.loads(self.attachments or "[]"),
            "is_read": self.is_read,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "created_at": self.created_at.isoformat()
        }


# -----------------------------------------
# CONNECTION MODEL
# -----------------------------------------
class Connection(db.Model):
    __tablename__ = "connections"

    id = db.Column(db.Integer, primary_key=True)
    
    requester_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    status = db.Column(db.String(50), default="pending")
    # pending, accepted, rejected, blocked
    
    message = db.Column(db.Text)  # Optional connection request message
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    accepted_at = db.Column(db.DateTime)

    # Relationships
    requester = db.relationship("User", foreign_keys=[requester_id], backref="connection_requests_sent")
    recipient = db.relationship("User", foreign_keys=[recipient_id], backref="connection_requests_received")

    def to_dict(self):
        return {
            "id": self.id,
            "requester_id": self.requester_id,
            "requester_name": self.requester.name if self.requester else None,
            "requester_profile_pic": self.requester.profile_pic if self.requester else None,
            "requester_role": self.requester.role if self.requester else None,
            "requester_company": self.requester.company if self.requester else None,
            "recipient_id": self.recipient_id,
            "recipient_name": self.recipient.name if self.recipient else None,
            "status": self.status,
            "message": self.message,
            "created_at": self.created_at.isoformat(),
            "accepted_at": self.accepted_at.isoformat() if self.accepted_at else None
        }


# -----------------------------------------
# ACHIEVEMENT MODEL
# -----------------------------------------
class Achievement(db.Model):
    __tablename__ = "achievements"

    id = db.Column(db.Integer, primary_key=True)
    
    code = db.Column(db.String(100), unique=True, nullable=False)  # early_mover, speed_demon, etc.
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))  # Font Awesome icon class
    
    # Unlock criteria (JSON)
    criteria = db.Column(db.Text)  # {"type": "application_count", "value": 1}
    
    # Rewards
    points = db.Column(db.Integer, default=0)
    badge_color = db.Column(db.String(50))
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "criteria": json.loads(self.criteria or "{}"),
            "points": self.points,
            "badge_color": self.badge_color
        }


# -----------------------------------------
# USER ACHIEVEMENT MODEL (Earned badges)
# -----------------------------------------
class UserAchievement(db.Model):
    __tablename__ = "user_achievements"

    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey("achievements.id"), nullable=False)
    
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress = db.Column(db.Integer, default=100)  # Percentage for partial achievements

    # Relationships
    user = db.relationship("User", backref="earned_achievements")
    achievement = db.relationship("Achievement", backref="user_earnings")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "achievement_id": self.achievement_id,
            "achievement": self.achievement.to_dict() if self.achievement else None,
            "earned_at": self.earned_at.isoformat(),
            "progress": self.progress
        }


# -----------------------------------------
# TEMPLATE MODEL
# -----------------------------------------
class Template(db.Model):
    __tablename__ = "templates"

    id = db.Column(db.Integer, primary_key=True)
    
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))  # pitch_deck, financial_model, one_pager, etc.
    
    # Template file
    file_url = db.Column(db.String(500))
    preview_image_url = db.Column(db.String(500))
    
    # Metadata
    usage_count = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=0.0)
    tags = db.Column(db.Text)  # JSON list
    
    # Access control
    is_premium = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    created_by = db.relationship("User", backref="created_templates")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "file_url": self.file_url,
            "preview_image_url": self.preview_image_url,
            "usage_count": self.usage_count,
            "rating": self.rating,
            "tags": json.loads(self.tags or "[]"),
            "is_premium": self.is_premium,
            "created_at": self.created_at.isoformat()
        }


# -----------------------------------------
# ONBOARDING PROGRESS MODEL
# -----------------------------------------
class OnboardingProgress(db.Model):
    __tablename__ = "onboarding_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    
    # Onboarding steps completed
    completed_steps = db.Column(db.Text)  # JSON list of step codes
    current_step = db.Column(db.String(100))
    
    # Progress tracking
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    
    # Tour preferences
    skip_tour = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("onboarding_progress", uselist=False))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "completed_steps": json.loads(self.completed_steps or "[]"),
            "current_step": self.current_step,
            "is_completed": self.is_completed,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "skip_tour": self.skip_tour
        }


# -----------------------------------------
# TWO-FACTOR AUTHENTICATION MODEL
# -----------------------------------------
class TwoFactorAuth(db.Model):
    __tablename__ = "two_factor_auth"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    
    # TOTP secret
    secret = db.Column(db.String(100), nullable=False)
    
    # Backup codes (JSON list)
    backup_codes = db.Column(db.Text)
    
    # Status
    is_enabled = db.Column(db.Boolean, default=False)
    enabled_at = db.Column(db.DateTime)
    
    # Recovery
    last_used_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("two_factor_auth", uselist=False))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "is_enabled": self.is_enabled,
            "enabled_at": self.enabled_at.isoformat() if self.enabled_at else None,
            "has_backup_codes": bool(self.backup_codes)
        }


# -----------------------------------------
# USER SESSION MODEL
# -----------------------------------------
class UserSession(db.Model):
    __tablename__ = "user_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    session_token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    
    # Device info
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    device_type = db.Column(db.String(50))  # desktop, mobile, tablet
    browser = db.Column(db.String(100))
    os = db.Column(db.String(100))
    
    # Session status
    is_active = db.Column(db.Boolean, default=True)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

    user = db.relationship("User", backref="sessions")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "device_type": self.device_type,
            "browser": self.browser,
            "os": self.os,
            "is_active": self.is_active,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "created_at": self.created_at.isoformat()
        }


# -----------------------------------------
# REWARD TRANSACTION MODEL (Enabler Rewards)
# -----------------------------------------
class RewardTransaction(db.Model):
    __tablename__ = "reward_transactions"

    id = db.Column(db.Integer, primary_key=True)
    enabler_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    referral_id = db.Column(db.Integer, db.ForeignKey("referrals.id"), nullable=True)
    
    # Transaction type
    type = db.Column(db.String(20), nullable=False)  # cash, points, bonus, payout, penalty
    
    # Amounts
    amount_money = db.Column(db.Float, default=0.0)  # In INR
    amount_points = db.Column(db.Integer, default=0)  # FLC Points
    
    # Status
    status = db.Column(db.String(20), default="pending")  # pending, settled, paid, failed, cancelled
    
    # Payout details
    payout_method = db.Column(db.String(50))  # wallet, bank_transfer, upi, points
    payout_reference = db.Column(db.String(200))  # Transaction ID from payment gateway
    
    # Program/Startup info
    startup_name = db.Column(db.String(200))
    program_name = db.Column(db.String(200))
    
    # Notes
    description = db.Column(db.Text)
    admin_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    settled_at = db.Column(db.DateTime)
    paid_at = db.Column(db.DateTime)

    enabler = db.relationship("User", backref="reward_transactions")
    referral = db.relationship("Referral", backref="reward_transactions")

    def to_dict(self):
        return {
            "id": self.id,
            "enabler_id": self.enabler_id,
            "referral_id": self.referral_id,
            "type": self.type,
            "amount_money": self.amount_money,
            "amount_points": self.amount_points,
            "status": self.status,
            "payout_method": self.payout_method,
            "startup_name": self.startup_name,
            "program_name": self.program_name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "settled_at": self.settled_at.isoformat() if self.settled_at else None,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None
        }


# -----------------------------------------
# ENABLER ANALYTICS MODEL (Daily Aggregates)
# -----------------------------------------
class EnablerAnalytics(db.Model):
    __tablename__ = "enabler_analytics"

    id = db.Column(db.Integer, primary_key=True)
    enabler_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    
    # Referral metrics
    referrals_count = db.Column(db.Integer, default=0)
    referrals_accepted = db.Column(db.Integer, default=0)
    referrals_rejected = db.Column(db.Integer, default=0)
    referrals_successful = db.Column(db.Integer, default=0)
    
    # Link tracking metrics
    clicks_count = db.Column(db.Integer, default=0)
    unique_clicks_count = db.Column(db.Integer, default=0)
    conversions_count = db.Column(db.Integer, default=0)
    
    # Financial metrics
    earnings_amount = db.Column(db.Float, default=0.0)
    pending_amount = db.Column(db.Float, default=0.0)
    points_earned = db.Column(db.Integer, default=0)
    
    # Performance metrics
    conversion_rate = db.Column(db.Float, default=0.0)  # Percentage
    avg_decision_time = db.Column(db.Integer, default=0)  # Days
    
    # Sector breakdown (JSON)
    sector_stats = db.Column(db.Text)  # {"HealthTech": {"referrals": 5, "conversions": 2}, ...}
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    enabler = db.relationship("User", backref="analytics_records")

    # Unique constraint on enabler_id + date
    __table_args__ = (
        db.UniqueConstraint('enabler_id', 'date', name='unique_enabler_date'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "enabler_id": self.enabler_id,
            "date": self.date.isoformat(),
            "referrals_count": self.referrals_count,
            "referrals_accepted": self.referrals_accepted,
            "referrals_successful": self.referrals_successful,
            "clicks_count": self.clicks_count,
            "conversions_count": self.conversions_count,
            "earnings_amount": self.earnings_amount,
            "pending_amount": self.pending_amount,
            "points_earned": self.points_earned,
            "conversion_rate": self.conversion_rate,
            "sector_stats": json.loads(self.sector_stats or "{}")
        }


# -----------------------------------------
# ENABLER LEVEL MODEL (Gamification)
# -----------------------------------------
class EnablerLevel(db.Model):
    __tablename__ = "enabler_levels"

    id = db.Column(db.Integer, primary_key=True)
    enabler_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    
    # Level and points
    level = db.Column(db.Integer, default=1)
    points = db.Column(db.Integer, default=0)
    
    # Tier system
    tier = db.Column(db.String(20), default="bronze")  # bronze, silver, gold, platinum, diamond
    
    # Stats for level calculation
    total_referrals = db.Column(db.Integer, default=0)
    successful_referrals = db.Column(db.Integer, default=0)
    total_earnings = db.Column(db.Float, default=0.0)
    
    # Achievements
    badges_earned = db.Column(db.Text)  # JSON list of badge codes
    
    # Ranking
    rank = db.Column(db.Integer)  # Overall rank among enablers
    percentile = db.Column(db.Float)  # Top X%
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_level_up = db.Column(db.DateTime)

    enabler = db.relationship("User", backref=db.backref("enabler_level", uselist=False))

    def to_dict(self):
        return {
            "id": self.id,
            "enabler_id": self.enabler_id,
            "level": self.level,
            "points": self.points,
            "tier": self.tier,
            "total_referrals": self.total_referrals,
            "successful_referrals": self.successful_referrals,
            "total_earnings": self.total_earnings,
            "badges_earned": json.loads(self.badges_earned or "[]"),
            "rank": self.rank,
            "percentile": self.percentile,
            "last_level_up": self.last_level_up.isoformat() if self.last_level_up else None
        }

    def calculate_level(self):
        """Calculate level based on points"""
        # Level thresholds: 1000 points per level
        new_level = max(1, self.points // 1000)
        if new_level > self.level:
            self.level = new_level
            self.last_level_up = datetime.utcnow()
        return self.level

    def calculate_tier(self):
        """Calculate tier based on performance"""
        if self.total_earnings >= 500000:  # ₹5 lakh+
            self.tier = "diamond"
        elif self.total_earnings >= 200000:  # ₹2 lakh+
            self.tier = "platinum"
        elif self.total_earnings >= 100000:  # ₹1 lakh+
            self.tier = "gold"
        elif self.total_earnings >= 50000:  # ₹50k+
            self.tier = "silver"
        else:
            self.tier = "bronze"
        return self.tier


# -----------------------------------------
# CORPORATE MODELS
# -----------------------------------------

# -----------------------------------------
# STARTUP MATCH MODEL (Corporate-Startup Matching)
# -----------------------------------------
class StartupMatch(db.Model):
    __tablename__ = "startup_matches"

    id = db.Column(db.Integer, primary_key=True)
    corporate_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    startup_id = db.Column(db.Integer, db.ForeignKey("startups.id"), nullable=False)
    
    # Match scoring
    match_score = db.Column(db.Float, default=0.0)  # 0-100
    match_factors = db.Column(db.Text)  # JSON: {"sector": 0.4, "stage": 0.3, "location": 0.2, "funding": 0.1}
    
    # Interaction tracking
    status = db.Column(db.String(50), default="discovered")  # discovered, viewed, contacted, connected, rejected
    viewed_at = db.Column(db.DateTime)
    contacted_at = db.Column(db.DateTime)
    connected_at = db.Column(db.DateTime)
    
    # Notes
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    corporate = db.relationship("User", foreign_keys=[corporate_id], backref="startup_matches")
    startup = db.relationship("Startup", backref="corporate_matches")

    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('corporate_id', 'startup_id', name='unique_corporate_startup_match'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "corporate_id": self.corporate_id,
            "startup_id": self.startup_id,
            "match_score": self.match_score,
            "match_factors": json.loads(self.match_factors or "{}"),
            "status": self.status,
            "viewed_at": self.viewed_at.isoformat() if self.viewed_at else None,
            "contacted_at": self.contacted_at.isoformat() if self.contacted_at else None,
            "connected_at": self.connected_at.isoformat() if self.connected_at else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


# -----------------------------------------
# DEAL MODEL (Corporate Deal Flow Pipeline)
# -----------------------------------------
class Deal(db.Model):
    __tablename__ = "deals"

    id = db.Column(db.Integer, primary_key=True)
    corporate_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    startup_id = db.Column(db.Integer, db.ForeignKey("startups.id"), nullable=False)
    
    # Deal information
    name = db.Column(db.String(200), nullable=False)  # Deal name/title
    stage = db.Column(db.String(50), default="new")  # new, contacted, dd, pilot, closed_won, closed_lost
    
    # Financial
    value = db.Column(db.Float, default=0.0)  # Deal value in currency
    probability = db.Column(db.Float, default=0.0)  # 0-100 probability of closing
    expected_close_date = db.Column(db.Date)
    
    # Details
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Next actions
    next_action = db.Column(db.String(200))
    next_action_date = db.Column(db.DateTime)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    closed_at = db.Column(db.DateTime)
    close_reason = db.Column(db.Text)  # Why won/lost
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    corporate = db.relationship("User", foreign_keys=[corporate_id], backref="deals")
    startup = db.relationship("Startup", backref="deals")

    def to_dict(self):
        return {
            "id": self.id,
            "corporate_id": self.corporate_id,
            "startup_id": self.startup_id,
            "name": self.name,
            "stage": self.stage,
            "value": self.value,
            "probability": self.probability,
            "expected_close_date": self.expected_close_date.isoformat() if self.expected_close_date else None,
            "description": self.description,
            "notes": self.notes,
            "next_action": self.next_action,
            "next_action_date": self.next_action_date.isoformat() if self.next_action_date else None,
            "is_active": self.is_active,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "close_reason": self.close_reason,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


# -----------------------------------------
# DEAL ACTIVITY MODEL (Deal History Tracking)
# -----------------------------------------
class DealActivity(db.Model):
    __tablename__ = "deal_activities"

    id = db.Column(db.Integer, primary_key=True)
    deal_id = db.Column(db.Integer, db.ForeignKey("deals.id"), nullable=False)
    
    # Activity details
    activity_type = db.Column(db.String(50), nullable=False)  # stage_change, note, meeting, email, call, document
    description = db.Column(db.Text)
    
    # Stage change tracking
    old_stage = db.Column(db.String(50))
    new_stage = db.Column(db.String(50))
    
    # User tracking
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    deal = db.relationship("Deal", backref="activities")
    user = db.relationship("User", foreign_keys=[created_by])

    def to_dict(self):
        return {
            "id": self.id,
            "deal_id": self.deal_id,
            "activity_type": self.activity_type,
            "description": self.description,
            "old_stage": self.old_stage,
            "new_stage": self.new_stage,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat()
        }


# -----------------------------------------
# CORPORATE PROFILE MODEL (Extended Corporate Info)
# -----------------------------------------
class CorporateProfile(db.Model):
    __tablename__ = "corporate_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    
    # Company information
    company_name = db.Column(db.String(200))
    industry = db.Column(db.String(100))
    company_size = db.Column(db.String(50))  # 1-10, 11-50, 51-200, 201-500, 501+
    website = db.Column(db.String(400))
    
    # Innovation focus
    innovation_focus = db.Column(db.Text)  # JSON list: ["AI", "CleanTech", "HealthTech"]
    innovation_thesis = db.Column(db.Text)  # Description of innovation strategy
    
    # Investment preferences
    investment_range_min = db.Column(db.Float)
    investment_range_max = db.Column(db.Float)
    preferred_stages = db.Column(db.Text)  # JSON list: ["Seed", "Series A"]
    preferred_sectors = db.Column(db.Text)  # JSON list
    preferred_regions = db.Column(db.Text)  # JSON list
    
    # Engagement preferences
    engagement_types = db.Column(db.Text)  # JSON list: ["POC", "Pilot", "Investment", "Partnership"]
    
    # Contact information
    job_title = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    
    # Notification settings
    notify_new_matches = db.Column(db.Boolean, default=True)
    notify_deal_updates = db.Column(db.Boolean, default=True)
    notify_applications = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("corporate_profile", uselist=False))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "company_name": self.company_name,
            "industry": self.industry,
            "company_size": self.company_size,
            "website": self.website,
            "innovation_focus": json.loads(self.innovation_focus or "[]"),
            "innovation_thesis": self.innovation_thesis,
            "investment_range_min": self.investment_range_min,
            "investment_range_max": self.investment_range_max,
            "preferred_stages": json.loads(self.preferred_stages or "[]"),
            "preferred_sectors": json.loads(self.preferred_sectors or "[]"),
            "preferred_regions": json.loads(self.preferred_regions or "[]"),
            "engagement_types": json.loads(self.engagement_types or "[]"),
            "job_title": self.job_title,
            "phone": self.phone,
            "notify_new_matches": self.notify_new_matches,
            "notify_deal_updates": self.notify_deal_updates,
            "notify_applications": self.notify_applications,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


# -----------------------------------------
# CORPORATE ANALYTICS MODEL (Activity Tracking)
# -----------------------------------------
class CorporateAnalytics(db.Model):
    __tablename__ = "corporate_analytics"

    id = db.Column(db.Integer, primary_key=True)
    corporate_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    
    # Startup discovery metrics
    startups_viewed = db.Column(db.Integer, default=0)
    startups_contacted = db.Column(db.Integer, default=0)
    startups_connected = db.Column(db.Integer, default=0)
    
    # Deal flow metrics
    deals_created = db.Column(db.Integer, default=0)
    deals_moved = db.Column(db.Integer, default=0)
    deals_closed_won = db.Column(db.Integer, default=0)
    deals_closed_lost = db.Column(db.Integer, default=0)
    
    # Application metrics
    applications_reviewed = db.Column(db.Integer, default=0)
    applications_shortlisted = db.Column(db.Integer, default=0)
    applications_rejected = db.Column(db.Integer, default=0)
    
    # Financial metrics
    total_deal_value = db.Column(db.Float, default=0.0)
    closed_deal_value = db.Column(db.Float, default=0.0)
    
    # Engagement metrics
    meetings_scheduled = db.Column(db.Integer, default=0)
    messages_sent = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    corporate = db.relationship("User", backref="corporate_analytics_records")

    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('corporate_id', 'date', name='unique_corporate_date'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "corporate_id": self.corporate_id,
            "date": self.date.isoformat(),
            "startups_viewed": self.startups_viewed,
            "startups_contacted": self.startups_contacted,
            "startups_connected": self.startups_connected,
            "deals_created": self.deals_created,
            "deals_moved": self.deals_moved,
            "deals_closed_won": self.deals_closed_won,
            "deals_closed_lost": self.deals_closed_lost,
            "applications_reviewed": self.applications_reviewed,
            "applications_shortlisted": self.applications_shortlisted,
            "applications_rejected": self.applications_rejected,
            "total_deal_value": self.total_deal_value,
            "closed_deal_value": self.closed_deal_value,
            "meetings_scheduled": self.meetings_scheduled,
            "messages_sent": self.messages_sent,
            "created_at": self.created_at.isoformat()
        }


# -----------------------------------------
# SECURITY LOG MODEL (Audit Logging)
# -----------------------------------------
class SecurityLog(db.Model):
    __tablename__ = "security_logs"

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(100), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    details = db.Column(db.Text)
    severity = db.Column(db.String(20), default="info")  # info, warning, error, critical
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationship
    user = db.relationship("User", backref="security_logs")

    def to_dict(self):
        return {
            "id": self.id,
            "event_type": self.event_type,
            "user_id": self.user_id,
            "user_name": self.user.name if self.user else None,
            "details": self.details,
            "severity": self.severity,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat()
        }
