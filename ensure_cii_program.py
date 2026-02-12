#!/usr/bin/env python3
"""
Ensure CII Program Exists in Database
This script can be run on deployment to ensure the CII program is present
"""

from extensions import db
from models import Opportunity, User
from app import create_app
from datetime import datetime
import json

def ensure_cii_program():
    """Add CII program if it doesn't exist"""
    app = create_app()
    with app.app_context():
        # Check if program already exists
        existing = Opportunity.query.filter_by(
            title="Capacity Building for Micro Entrepreneurs with Disabilities"
        ).first()
        
        if existing:
            print("✅ CII program already exists in database")
            print(f"   ID: {existing.id}")
            print(f"   Status: {existing.status}")
            return existing
        
        print("📝 CII program not found. Adding it now...")
        
        # Find a corporate user to be the owner (or use first user)
        corporate_user = User.query.filter_by(role='corporate').first()
        if not corporate_user:
            corporate_user = User.query.first()
        
        if not corporate_user:
            print("❌ No users found in database. Cannot add program.")
            return None
        
        # Create the program
        program = Opportunity()
        program.owner_id = corporate_user.id
        program.title = "Capacity Building for Micro Entrepreneurs with Disabilities"
        program.type = "capacity-building"
        program.description = """Confederation of Indian Industry (CII), through its new Centre of Excellence on Employment and Livelihood (CII CEL), in collaboration with CII Foundation, IBDN, and supported by NatWest Group, has launched a special program for Entrepreneurs with Disabilities.

This initiative aims to empower entrepreneurs to scale their businesses through capacity building, mentorship, and continuous guidance.

Program Highlights:
• Business 360° Capacity Building in Tamil & English
• Practical tools, workbooks, and curated curriculum
• Mentorship from CII Corporate & Industry experts
• Networking with business peers
• Handholding support for 6 months to 1 year

Workshop Highlights:
Practical sessions on leadership, sales growth, employee management, finance, cashflow, and digital transformation using AI."""
        
        program.eligibility = """Who can attend:
• Entrepreneurs with disabilities
• Enterprises led by differently abled persons
• Enterprise can be in Manufacturing, Services or Trading
• Family business owners with their partners, siblings, and spouses

Prior Registration is Mandatory. Only Shortlisted Members Will Receive The confirmation."""
        
        program.benefits = """• Business 360° Capacity Building in Tamil & English
• Practical tools, workbooks, and curated curriculum
• Mentorship from CII Corporate & Industry experts
• Networking with business peers
• Handholding support for 6 months to 1 year
• Practical sessions on leadership, sales growth, employee management
• Finance and cashflow management training
• Digital transformation using AI guidance"""
        
        program.sectors = json.dumps([
            "disability-entrepreneurship", 
            "micro-enterprise", 
            "manufacturing", 
            "services", 
            "trading",
            "capacity-building",
            "inclusive-business"
        ])
        
        program.target_stages = json.dumps([
            "micro-business",
            "early-stage", 
            "growth-stage",
            "family-business"
        ])
        
        program.countries = json.dumps(["India"])
        program.deadline = datetime(2025, 10, 31)
        program.banner_url = "https://images.unsplash.com/photo-1573164713714-d95e436ab8d6?q=80&w=2069&auto=format&fit=crop"
        program.status = "published"
        
        db.session.add(program)
        db.session.commit()
        
        print("✅ Successfully added CII Capacity Building program!")
        print(f"   ID: {program.id}")
        print(f"   Title: {program.title}")
        print(f"   Status: {program.status}")
        
        return program

if __name__ == "__main__":
    result = ensure_cii_program()
    if result:
        print("\n🎉 CII program is ready!")
    else:
        print("\n❌ Failed to ensure CII program")
