#!/usr/bin/env python3
"""
Script to add more opportunities to the database for testing
"""

from extensions import db
from models import Opportunity, User
from app import create_app
from datetime import datetime, timedelta
import json

def add_opportunities():
    app = create_app()
    with app.app_context():
        # Find a corporate user to be the owner
        corporate_user = User.query.filter_by(role='corporate').first()
        if not corporate_user:
            print("No corporate user found. Creating one...")
            corporate_user = User(
                name="Test Corporate",
                email="corporate@test.com",
                role="corporate",
                company="Test Corp",
                country="Global"
            )
            corporate_user.set_password("password123")
            db.session.add(corporate_user)
            db.session.commit()
        
        # List of opportunities to add
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
                "title": "Sustainable Energy Accelerator",
                "type": "accelerator",
                "description": "6-month program for clean energy startups working on renewable energy, energy storage, and smart grid solutions.",
                "eligibility": "Clean energy startups with working prototypes",
                "benefits": "$75k funding + technical mentorship + pilot opportunities",
                "sectors": ["cleantech", "energy", "sustainability"],
                "target_stages": ["seed", "series-a"],
                "countries": ["Germany", "Netherlands", "Denmark"],
                "banner_url": "https://images.unsplash.com/photo-1466611653911-95081537e5b7?q=80&w=2070&auto=format&fit=crop"
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
                "title": "Retail Innovation Lab",
                "type": "lab",
                "description": "Partnership program for retail technology startups to pilot solutions with major retail chains.",
                "eligibility": "Retail tech startups with B2B focus and scalable solutions",
                "benefits": "Pilot contracts + retail network access + go-to-market support",
                "sectors": ["retail", "e-commerce", "supply-chain"],
                "target_stages": ["series-a", "series-b"],
                "countries": ["USA", "UK", "France"],
                "banner_url": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?q=80&w=2070&auto=format&fit=crop"
            },
            {
                "title": "AgriTech Innovation Program",
                "type": "program",
                "description": "Supporting agricultural technology startups with precision farming, crop monitoring, and sustainable agriculture solutions.",
                "eligibility": "AgriTech startups with field-tested solutions",
                "benefits": "$40k grant + farm partnerships + distribution channels",
                "sectors": ["agritech", "agriculture", "sustainability"],
                "target_stages": ["seed", "series-a"],
                "countries": ["Brazil", "India", "Kenya"],
                "banner_url": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?q=80&w=2069&auto=format&fit=crop"
            },
            {
                "title": "EdTech Transformation Initiative",
                "type": "initiative",
                "description": "Accelerating educational technology startups focused on online learning, skill development, and educational content.",
                "eligibility": "EdTech startups with proven user engagement and learning outcomes",
                "benefits": "$60k funding + educational partnerships + content distribution",
                "sectors": ["edtech", "education", "e-learning"],
                "target_stages": ["seed", "series-a"],
                "countries": ["Global"],
                "banner_url": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=2071&auto=format&fit=crop"
            },
            {
                "title": "Smart City Solutions Hub",
                "type": "hub",
                "description": "Connecting urban technology startups with city governments for smart infrastructure and citizen services.",
                "eligibility": "Smart city startups with government-ready solutions",
                "benefits": "Government contracts + regulatory support + scaling opportunities",
                "sectors": ["smart-city", "iot", "urban-tech"],
                "target_stages": ["series-a", "series-b"],
                "countries": ["UAE", "Singapore", "Estonia"],
                "banner_url": "https://images.unsplash.com/photo-1480714378408-67cf0d13bc1f?q=80&w=2070&auto=format&fit=crop"
            },
            {
                "title": "Cybersecurity Innovation Challenge",
                "type": "challenge",
                "description": "Seeking next-generation cybersecurity solutions for enterprise and government applications.",
                "eligibility": "Cybersecurity startups with enterprise-grade solutions",
                "benefits": "$80k pilot funding + enterprise customers + security certifications",
                "sectors": ["cybersecurity", "enterprise", "government"],
                "target_stages": ["series-a", "series-b"],
                "countries": ["USA", "Israel", "UK"],
                "banner_url": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=2070&auto=format&fit=crop"
            },
            {
                "title": "Space Technology Accelerator",
                "type": "accelerator",
                "description": "Supporting space technology startups with satellite technology, space exploration, and aerospace innovations.",
                "eligibility": "Space tech startups with technical expertise and space applications",
                "benefits": "$120k funding + space agency partnerships + launch opportunities",
                "sectors": ["space-tech", "aerospace", "satellites"],
                "target_stages": ["seed", "series-a"],
                "countries": ["USA", "France", "Japan"],
                "banner_url": "https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?q=80&w=2071&auto=format&fit=crop"
            }
        ]
        
        added_count = 0
        for opp_data in opportunities:
            # Check if opportunity already exists
            existing = Opportunity.query.filter_by(title=opp_data["title"]).first()
            if existing:
                print(f"Opportunity '{opp_data['title']}' already exists, skipping...")
                continue
            
            # Create new opportunity
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
                deadline=datetime.utcnow() + timedelta(days=60),  # 60 days from now
                banner_url=opp_data["banner_url"],
                status="published"
            )
            
            db.session.add(new_opp)
            added_count += 1
            print(f"Added opportunity: {opp_data['title']}")
        
        db.session.commit()
        print(f"\n✅ Successfully added {added_count} new opportunities!")
        
        # Show total count
        total_opps = Opportunity.query.count()
        published_opps = Opportunity.query.filter_by(status="published").count()
        print(f"Total opportunities in database: {total_opps}")
        print(f"Published opportunities: {published_opps}")

if __name__ == "__main__":
    add_opportunities()