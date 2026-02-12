"""
Pytest Configuration and Fixtures
Provides common test fixtures and configuration for all tests
"""

import pytest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db
from models import User, Startup, Opportunity, Meeting, MeetingParticipant, Notification
from datetime import datetime, timedelta


@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    # Set testing configuration
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'  # In-memory database for tests
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    return app


@pytest.fixture(scope='function')
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Create database session for testing"""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        name="Test User",
        email="test@example.com",
        role="startup"
    )
    user.set_password("password123")
    db_session.session.add(user)
    db_session.session.commit()
    return user


@pytest.fixture
def test_admin(db_session):
    """Create a test admin user"""
    admin = User(
        name="Admin User",
        email="admin@example.com",
        role="admin"
    )
    admin.set_password("admin123")
    db_session.session.add(admin)
    db_session.session.commit()
    return admin


@pytest.fixture
def test_startup(db_session, test_user):
    """Create a test startup"""
    startup = Startup(
        founder_id=test_user.id,
        name="Test Startup Inc",
        description="A test startup for testing purposes",
        location="San Francisco, CA",
        sectors='["Technology", "AI"]',
        stage="MVP",
        team_size="5-10",
        founding_date=datetime.utcnow()
    )
    db_session.session.add(startup)
    db_session.session.commit()
    return startup


@pytest.fixture
def test_opportunity(db_session, test_admin):
    """Create a test opportunity"""
    opportunity = Opportunity(
        owner_id=test_admin.id,
        title="Test Accelerator Program",
        type="accelerator",
        description="A test accelerator program",
        sectors='["Technology"]',
        target_stages='["MVP", "Early"]',
        deadline=datetime.utcnow() + timedelta(days=30),
        status="published"
    )
    db_session.session.add(opportunity)
    db_session.session.commit()
    return opportunity


@pytest.fixture
def test_meeting(db_session, test_admin, test_user):
    """Create a test meeting"""
    meeting = Meeting(
        created_by_id=test_admin.id,
        title="Test Meeting",
        description="A test meeting",
        scheduled_at=datetime.utcnow() + timedelta(hours=1),
        duration_minutes=60,
        timezone="UTC",
        access_type="specific_users",
        meeting_room_id="TEST123",
        meeting_password="testpass"
    )
    db_session.session.add(meeting)
    db_session.session.flush()
    
    # Add participant
    participant = MeetingParticipant(
        meeting_id=meeting.id,
        user_id=test_user.id
    )
    db_session.session.add(participant)
    db_session.session.commit()
    
    return meeting


@pytest.fixture
def authenticated_client(client, test_user):
    """Create an authenticated test client"""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)
        sess['_fresh'] = True
    return client


@pytest.fixture
def admin_client(client, test_admin):
    """Create an authenticated admin client"""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_admin.id)
        sess['_fresh'] = True
    return client