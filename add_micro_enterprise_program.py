#!/usr/bin/env python3
"""
Script to add Capacity Building for Micro Enterprises program
"""

from extensions import db
from models import Opportunity, User
from app import create_app
from datetime import datetime, timedelta
import json

def add_micro_enterprise_program():
    app = create_app()
    with app.app_context():
        # Find a corporate user to be the owner
        corporate_user = User.query.filter_by(role='corporate').first()
        if not corporate_user:
            print("No corporate user found. Please create one first.")
            return
        
        # Check if program already exists
        existing = Opportunity.query.filter_by(title="Capacity Building for Micro Enterprises").first()
        if existing:
            print("Program 'Capacity Building for Micro Enterprises' already exists!")
            print(f"ID: {existing.id}")
            print(f"Status: {existing.status}")
            print(f"Type: {existing.type}")
            return
        
        # Create the micro enterprise capacity building program
        micro_enterprise_program = {
            "title": "Capacity Building for Micro Enterprises",
            "type": "capacity-building",
            "description": "Comprehensive capacity building program designed to empower micro enterprises with essential business skills, digital literacy, financial management, and market access strategies. This program focuses on sustainable growth and resilience building for small-scale entrepreneurs.",
            "eligibility": "Micro enterprises with less than 10 employees, annual revenue under $100k, and demonstrated commitment to business growth",
            "benefits": "Business training + mentorship + micro-financing access + digital tools + market linkage support + 6-month follow-up",
            "sectors": ["micro-enterprise", "small-business", "entrepreneurship", "capacity-building"],
            "target_stages": ["pre-revenue", "early-revenue", "micro-business"],
            "countries": ["India", "Bangladesh", "Kenya", "Nigeria", "Philippines", "Indonesia"],
            "banner_url": "https://images.unsplash.com/photo-1556761175-b413da4baf72?q=80&w=2074&auto=format&fit=crop"
        }
        
        # Create new opportunity
        new_program = Opportunity(
            owner_id=corporate_user.id,
            title=micro_enterprise_program["title"],
            type=micro_enterprise_program["type"],
            description=micro_enterprise_program["description"],
            eligibility=micro_enterprise_program["eligibility"],
            benefits=micro_enterprise_program["benefits"],
            sectors=json.dumps(micro_enterprise_program["sectors"]),
            target_stages=json.dumps(micro_enterprise_program["target_stages"]),
            countries=json.dumps(micro_enterprise_program["countries"]),
            deadline=datetime.now() + timedelta(days=90),  # 90 days from now
            banner_url=micro_enterprise_program["banner_url"],
            status="published"
        )
        
        db.session.add(new_program)
        db.session.commit()
        
        print("✅ Successfully added 'Capacity Building for Micro Enterprises' program!")
        print(f"Program ID: {new_program.id}")
        print(f"Title: {new_program.title}")
        print(f"Type: {new_program.type}")
        print(f"Status: {new_program.status}")
        print(f"Sectors: {micro_enterprise_program['sectors']}")
        print(f"Target Countries: {micro_enterprise_program['countries']}")
        
        # Show total count
        total_opps = Opportunity.query.count()
        published_opps = Opportunity.query.filter_by(status="published").count()
        print(f"\nTotal opportunities in database: {total_opps}")
        print(f"Published opportunities: {published_opps}")

if __name__ == "__main__":
    add_micro_enterprise_program()