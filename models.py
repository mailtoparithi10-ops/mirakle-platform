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
