# create_db.py
from app import create_app
from extensions import db
import os

app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    print("Database tables created (or already exist).")
