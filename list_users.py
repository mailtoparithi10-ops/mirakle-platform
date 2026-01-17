
from app import create_app
from extensions import db
from models import User

app = create_app()

with app.app_context():
    users = User.query.all()
    print("-" * 50)
    print(f"{'ID':<5} {'Name':<20} {'Email':<30} {'Role':<15}")
    print("-" * 50)
    for u in users:
        print(f"{u.id:<5} {u.name:<20} {u.email:<30} {u.role:<15}")
    print("-" * 50)
