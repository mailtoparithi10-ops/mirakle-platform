#!/usr/bin/env python3
"""
Deployment script to set up data on Render after deployment
This should be run once after the app is deployed to Render
"""

import os
from extensions import db
from models import User, Opportunity
from app import create_app
from datetime import datetime, timedelta
import json

def setup_render_data():
    """Set up initial data for Render deployment"""
    app = create_app()
    
    with app.app_context():
        print("🚀 Setting up data for Render deployment...")
        
        # Create tables if they don't exist
        db.create_all()
        print("✅ Database tables created/verified")
        
        # 1. Create admin user
        admin_user = User.query.filter_by(email="admin@test.com").first()
        if not admin_user:
            admin_user = User(
                name="Admin User",
                email="admin@test.com",
                role="admin",
                company="InnoBridge Platform",
                country="Global",
                is_active=True
            )
            admin_user.set_password("admin123")
            db.session.add(admin_user)
            print("✅ Created admin user")
        
        # 2. Create test users
        test_users = [
            {
                "name": "Startup User",
                "email": "startup@test.com",
                "password": "startup123",
                "role": "startup",
                "company": "Test Startup Inc",
                "country": "USA"
            },
            {
                "name": "Corporate User", 
                "email": "corporate@test.com",
                "password": "corporate123",
                "role": "corporate",
                "company": "Test Corporation",
                "country": "USA"
            },
            {
                "name": "Connector User",
                "email": "connector@test.com", 
                "password": "connector123",
                "role": "connector",
                "company": "Test Connector Hub",
                "country": "India"
            }
        ]
        
        for user_data in test_users:
            existing_user = User.query.filter_by(email=user_data["email"]).first()
            if not existing_user:
                new_user = User(
                    name=user_data["name"],
                    email=user_data["email"],
                    role=user_data["role"],
                    company=user_data["company"],
                    country=user_data["country"],
                    is_active=True
                )
                new_user.set_password(user_data["password"])
                db.session.add(new_user)
                print(f"✅ Created {user_data['role']} user: {user_data['email']}")
        
        db.session.commit()
        
        # 3. Find corporate user for opportunities
        corporate_user = User.query.filter_by(role='corporate').first()
        if not corporate_user:
            print("❌ No corporate user found, cannot create opportunities")
            return
        
        # 4. Create opportunities
        opportunities = [
            {
                "title": "Global Fintech Accelerator 2026",
                "type": "accelerator",
                "description": "A 3-month program for early-stage fintech startups focusing on cross-border payments, digital banking, and blockchain solutions.",
                "eligibility": "Early-stage fintech startups with MVP and initial traction",
                "benefits": "$50k equity-free grant + mentorship + access to banking partners",
                "sectors": ["fintech", "blockchain", "payments"],
                "target_stages": ["seed", "pre-series-a"],
                "countries": ["Global"],
                "banner_url": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?q=80&w=1965&auto=format&fit=crop"
            },
            {
                "title": "HealthTech Innovation Challenge",
                "type": "challenge",
                "description": "Seeking innovative healthcare solutions for remote patient monitoring and telemedicine platforms.",
                "eligibility": "Healthcare startups with proven technology and regulatory compliance",
                "benefits": "$100k pilot contract + hospital network access + regulatory support",
                "sectors": ["healthtech", "medtech", "digital-health"],
                "target_stages": ["series-a", "series-b"],
                "countries": ["USA", "Canada", "UK"],
                "banner_url": "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?q=80&w=1931&auto=format&fit=crop"
            },
            {
                "title": "Capacity Building for Micro Entrepreneurs with Disabilities",
                "type": "capacity-building",
                "description": "Confederation of Indian Industry (CII), through its new Centre of Excellence on Employment and Livelihood (CII CEL), in collaboration with CII Foundation, IBDN, and supported by NatWest Group, has launched a special program for Entrepreneurs with Disabilities. This initiative aims to empower entrepreneurs to scale their businesses through capacity building, mentorship, and continuous guidance.",
                "eligibility": "Entrepreneurs with disabilities, Enterprises led by differently abled persons, Enterprise can be in Manufacturing, Services or Trading, Family business owners with their partners, siblings, and spouses",
                "benefits": "Business 360° Capacity Building in Tamil & English, Practical tools, workbooks, and curated curriculum, Mentorship from CII Corporate & Industry experts, Networking with business peers, Handholding support for 6 months to 1 year",
                "sectors": ["disability-entrepreneurship", "micro-enterprise", "manufacturing", "services", "trading", "capacity-building", "inclusive-business"],
                "target_stages": ["micro-business", "early-stage", "growth-stage", "family-business"],
                "countries": ["India"],
                "banner_url": "https://images.unsplash.com/photo-1573164713714-d95e436ab8d6?q=80&w=2069&auto=format&fit=crop"
            },
            {
                "title": "AI & Machine Learning Bootcamp",
                "type": "bootcamp",
                "description": "Intensive 12-week program for AI startups focusing on computer vision, NLP, and predictive analytics.",
                "eligibility": "AI/ML startups with technical team and initial product",
                "benefits": "$30k stipend + GPU credits + industry partnerships",
                "sectors": ["ai", "machine-learning", "computer-vision"],
                "target_stages": ["pre-seed", "seed"],
                "countries": ["Singapore", "India", "Australia"],
                "banner_url": "https://images.unsplash.com/photo-1555949963-aa79dcee981c?q=80&w=2070&auto=format&fit=crop"
            },
            {
                "title": "Sustainable Energy Accelerator",
                "type": "accelerator",
                "description": "6-month program for clean energy startups working on renewable energy, energy storage, and smart grid solutions.",
                "eligibility": "Clean energy startups with working prototypes",
                "benefits": "$75k funding + technical mentorship + pilot opportunities",
                "sectors": ["cleantech", "energy", "sustainability"],
                "target_stages": ["seed", "series-a"],
                "countries": ["Germany", "Netherlands", "Denmark"],
                "banner_url": "https://images.unsplash.com/photo-1466611653911-95081537e5b7?q=80&w=2070&auto=format&fit=crop"
            }
        ]
        
        opportunities_added = 0
        for opp_data in opportunities:
            existing = Opportunity.query.filter_by(title=opp_data["title"]).first()
            if not existing:
                new_opp = Opportunity(
                    owner_id=corporate_user.id,
                    title=opp_data["title"],
                    type=opp_data["type"],
                    description=opp_data["description"],
                    eligibility=opp_data["eligibility"],
                    benefits=opp_data["benefits"],
                    sectors=json.dumps(opp_data["sectors"]),
                    target_stages=json.dumps(opp_data["target_stages"]),
                    countries=json.dumps(opp_data["countries"]),
                    deadline=datetime.now() + timedelta(days=90),
                    banner_url=opp_data["banner_url"],
                    status="published"
                )
                db.session.add(new_opp)
                opportunities_added += 1
                print(f"✅ Created opportunity: {opp_data['title']}")
        
        db.session.commit()
        
        print(f"\n🎉 Render deployment setup complete!")
        print(f"✅ Added {opportunities_added} opportunities")
        print(f"✅ Total opportunities: {Opportunity.query.count()}")
        print(f"✅ Total users: {User.query.count()}")
        
        print(f"\n🔑 Login Credentials:")
        print(f"Admin: admin@test.com / admin123")
        print(f"Startup: startup@test.com / startup123") 
        print(f"Corporate: corporate@test.com / corporate123")
        print(f"Connector: connector@test.com / connector123")

if __name__ == "__main__":
    setup_render_data()