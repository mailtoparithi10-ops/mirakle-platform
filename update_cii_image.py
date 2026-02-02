#!/usr/bin/env python3
"""
Script to update the CII program with the correct uploaded image
"""

from extensions import db
from models import Opportunity
from app import create_app

def update_cii_image():
    app = create_app()
    with app.app_context():
        # Find the CII program
        program = Opportunity.query.filter_by(title="Capacity Building for Micro Entrepreneurs with Disabilities").first()
        
        if program:
            print(f"Found program: {program.title}")
            print(f"Current banner URL: {program.banner_url}")
            
            # Update with a more relevant professional image for disability entrepreneurship
            program.banner_url = "https://images.unsplash.com/photo-1573164713714-d95e436ab8d6?q=80&w=2069&auto=format&fit=crop"
            
            db.session.commit()
            
            print(f"✅ Updated banner URL to: {program.banner_url}")
            print("The CII program image should now display correctly!")
            
        else:
            print("CII program not found in database.")

if __name__ == "__main__":
    update_cii_image()