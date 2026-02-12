
from app import create_app
from extensions import db
from models import User, Startup
import json

app = create_app()

with app.app_context():
    # Create a test founder
    user = User.query.filter_by(email='founder@test.com').first()
    if not user:
        user = User(name='Test Founder', email='founder@test.com', role='founder')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        print(f"Created user: {user.email}")
    else:
        print(f"User exists: {user.email}")

    # Create a test startup
    startup = Startup.query.filter_by(founder_id=user.id).first()
    if not startup:
        startup = Startup(
            founder_id=user.id,
            name='Test Startup',
            description='A test startup description',
            sectors=json.dumps(['AI', 'FinTech']),
            stage='seed',
            application_status='draft'
        )
        db.session.add(startup)
        db.session.commit()
        print(f"Created startup: {startup.name}")
    else:
        print(f"Startup exists: {startup.name}")