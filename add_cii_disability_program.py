#!/usr/bin/env python3
"""
Script to add CII Capacity Building for Micro Entrepreneurs with Disabilities program
"""

from extensions import db
from models import Opportunity, User
from app import create_app
from datetime import datetime, timedelta
import json

def add_cii_program():
    app = create_app()
    with app.app_context():
        # Find a corporate user to be the owner
        corporate_user = User.query.filter_by(role='corporate').first()
        if not corporate_user:
            print("No corporate user found. Please create one first.")
            return
        
        # Check if program already exists
        existing = Opportunity.query.filter_by(title="Capacity Building for Micro Entrepreneurs with Disabilities").first()
        if existing:
            print("Program already exists! Updating it...")
            program = existing
        else:
            program = Opportunity()
            print("Creating new program...")
        
        # Program details based on the provided content
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
        
        program.countries = json.dumps([
            "India"
        ])
        
        # Set deadline to October 2025 as shown in the image
        program.deadline = datetime(2025, 10, 31)
        
        # Use a more relevant image for disability entrepreneurship and capacity building
        program.banner_url = "https://images.unsplash.com/photo-1573164713714-d95e436ab8d6?q=80&w=2069&auto=format&fit=crop"
        
        program.status = "published"
        
        if not existing:
            db.session.add(program)
        
        db.session.commit()
        
        print("✅ Successfully added CII Capacity Building program!")
        print(f"Program ID: {program.id}")
        print(f"Title: {program.title}")
        print(f"Type: {program.type}")
        print(f"Status: {program.status}")
        print(f"Deadline: {program.deadline}")
        print(f"Target Location: Chennai, Coimbatore, Madurai, Erode & Tirupur")
        
        # Show total count
        total_opps = Opportunity.query.count()
        published_opps = Opportunity.query.filter_by(status="published").count()
        print(f"\nTotal opportunities in database: {total_opps}")
        print(f"Published opportunities: {published_opps}")
        
        print(f"\nContact Details:")
        print(f"CS Dyana")
        print(f"cs.dyana@cii.in | +91 90436 88280")

if __name__ == "__main__":
    add_cii_program()