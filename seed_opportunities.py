
from app import create_app
from extensions import db
from models import Opportunity, User
from datetime import datetime, timedelta
import json

app = create_app()

def seed_opportunities():
    with app.app_context():
        # Clear existing opportunities
        print("Clearing existing opportunities...")
        try:
            db.session.query(Opportunity).delete()
            db.session.commit()
            print("Existing opportunities cleared.")
        except Exception as e:
            print(f"Error clearing opportunities: {e}")
            db.session.rollback()
            return

        # Ensure we have a valid owner (admin or corporate)
        owner = User.query.filter(User.role.in_(['admin', 'corporate'])).first()
        if not owner:
            # Fallback to any user if no admin/corporate exists, or create a dummy one
            owner = User.query.first()
            if not owner:
                print("No users found. Please create a user first.")
                return
        
        owner_id = owner.id
        print(f"Assigning opportunities to owner_id: {owner_id}")

        current_time = datetime.utcnow()

        opportunities_data = [
            {
                "title": "Y Combinator (S25 Batch)",
                "type": "accelerator",
                "description": "Y Combinator provides seed funding for startups. Seed funding is the earliest stage of venture funding. It pays your expenses while you’re getting started.",
                "eligibility": "Early-stage startups from all sectors.",
                "sectors": ["Technology", "SaaS", "Consumer", "B2B", "Healthcare", "Fintech"],
                "target_stages": ["Pre-Seed", "Seed"],
                "countries": ["Global", "USA"],
                "deadline": current_time + timedelta(days=60),
                "benefits": "$125k for 7% equity + $375k on an uncapped safe with an MFN.",
                "status": "published"
            },
            {
                "title": "Techstars Global Accelerator",
                "type": "accelerator",
                "description": "Techstars is the global network that helps entrepreneurs succeed. Techstars founders connect with other entrepreneurs, experts, mentors, alumni, investors, community leaders, and corporations to grow their companies.",
                "eligibility": "High-growth startups with a prototype or MVP.",
                "sectors": ["FinTech", "HealthTech", "CleanTech", "Web3", "AI"],
                "target_stages": ["Seed", "Series A"],
                "countries": ["Global", "USA", "Europe", "Asia"],
                "deadline": current_time + timedelta(days=45),
                "benefits": "$20k for 6% equity + $100k convertible note.",
                "status": "published"
            },
            {
                "title": "500 Global Flagship Accelerator",
                "type": "accelerator",
                "description": "500 Global is a venture capital firm with more than $2.7 billion in assets under management that invests in founders building fast-growing technology companies.",
                "eligibility": "Tech startups with significant traction.",
                "sectors": ["Technology", "SaaS", "E-commerce"],
                "target_stages": ["Seed", "Pre-Series A"],
                "countries": ["Global"],
                "deadline": current_time + timedelta(days=30),
                "benefits": "$150k investment for 6% equity.",
                "status": "closing_soon"
            },
            {
                "title": "Google for Startups Accelerator: AI First",
                "type": "accelerator",
                "description": "A 10-week equity-free hybrid program for Seed to Series A AI startups. The program offers access to Google's best-in-class expertise and technology.",
                "eligibility": "AI/ML focused startups leveraging AI/ML technologies.",
                "sectors": ["AI", "Machine Learning"],
                "target_stages": ["Seed", "Series A"],
                "countries": ["Global"],
                "deadline": current_time + timedelta(days=90),
                "benefits": "Equity-free support, Google product credits, mentorship.",
                "status": "published"
            },
            {
                "title": "Sanofi iNext 2025-2026 Challenge",
                "type": "pilot",
                "description": "A pitching competition seeking 'moon-shot' ideas to counter aging-related cellular dysfunction or strategies for targeted delivery of large molecules.",
                "eligibility": "Startups and academic labs in North America and Europe.",
                "sectors": ["HealthTech", "Biotech"],
                "target_stages": ["Seed", "Series A", "Research"],
                "countries": ["USA", "Europe", "Canada"],
                "deadline": current_time + timedelta(days=120),
                "benefits": "Partnership opportunities, pilot projects, and potential funding.",
                "status": "published"
            },
            {
                "title": "Orange Startup Challenge 2025",
                "type": "challenge",
                "description": "Seeking cutting-edge technologies that optimize performance, improve user experiences, and maximize AI's positive impact on society.",
                "eligibility": "Startups with solutions in AI, Telco, and Consumer Services.",
                "sectors": ["Telecommunications", "AI", "Consumer Tech"],
                "target_stages": ["Seed", "Series A"],
                "countries": ["Global", "Europe", "Africa"],
                "deadline": current_time + timedelta(days=70),
                "benefits": "Business leads, investor meetings, and visibility.",
                "status": "published"
            },
            {
                "title": "VivaTech 2025 Startup Challenge",
                "type": "challenge",
                "description": "Showcase your solutions at VivaTech, one of the world's biggest startup and tech events. Get feedback, business leads, and investor meetings.",
                "eligibility": "Innovative startups across all sectors.",
                "sectors": ["General", "Tech"],
                "target_stages": ["Pre-Seed", "Seed", "Series A", "Series B"],
                "countries": ["Global"],
                "deadline": current_time + timedelta(days=100),
                "benefits": "Free exhibition booth at VivaTech, networking.",
                "status": "published"
            },
            {
                "title": "Alchemist Accelerator",
                "type": "accelerator",
                "description": "A venture-backed accelerator focused on enterprise startups (B2B) that monetize from enterprises, not consumers.",
                "eligibility": "B2B enterprise startups.",
                "sectors": ["Enterprise", "B2B", "SaaS", "IoT"],
                "target_stages": ["Seed", "Series A"],
                "countries": ["Global", "USA"],
                "deadline": current_time + timedelta(days=50),
                "benefits": "Mentorship, $25k investment, network of enterprise customers.",
                "status": "published"
            },
            {
                "title": "Plug and Play Fintech Batch 2025",
                "type": "accelerator",
                "description": "Connecting the best startups with the world’s largest financial institutions. We help you scale through pilots, POCs, and investment.",
                "eligibility": "Fintech startups looking for corporate partnerships.",
                "sectors": ["FinTech", "InsurTech", "Crypto"],
                "target_stages": ["Seed", "Series A", "Growth"],
                "countries": ["Global"],
                "deadline": current_time + timedelta(days=15),
                "benefits": "Corporate pilots, no equity taken for participation.",
                "status": "closing_soon"
            },
            {
                "title": "Global Entrepreneurship Challenge 2025",
                "type": "challenge",
                "description": "Supported by the Tokyo Government, connecting international innovators with Japan's business ecosystem to launch and scale ventures.",
                "eligibility": "Startups interested in the Japanese market.",
                "sectors": ["Sustainability", "Digital Innovation", "Wellbeing", "Entertainment"],
                "target_stages": ["Seed", "Series A"],
                "countries": ["Global", "Japan"],
                "deadline": current_time + timedelta(days=150),
                "benefits": "Market entry support, funding, and mentorship.",
                "status": "published"
            },
            {
                "title": "MassChallenge Early Stage",
                "type": "accelerator",
                "description": "A global non-profit zero-equity accelerator. We connect startups with experts, corporations, and communities to grow and transform businesses.",
                "eligibility": "Early-stage startups from any industry.",
                "sectors": ["General", "HealthTech", "FinTech", "CleanTech"],
                "target_stages": ["Pre-Seed", "Seed"],
                "countries": ["Global", "USA", "Switzerland", "Mexico"],
                "deadline": current_time + timedelta(days=80),
                "benefits": "Equity-free, mentorship, office space, cash prizes.",
                "status": "published"
            },
             {
                "title": "NEC Innovation Challenge 2024",
                "type": "challenge",
                "description": "Calling for startups to collaborate on solutions in Healthcare, Sustainability, Digital Operational Excellence, and Media/Entertainment.",
                "eligibility": "Startups with relevance to NEC's focus areas.",
                "sectors": ["Healthcare", "Sustainability", "Media"],
                "target_stages": ["Seed", "Series A", "Series B"],
                "countries": ["Global"],
                "deadline": current_time + timedelta(days=40),
                "benefits": "Collaboration with NEC, expansion into Japanese Market.",
                "status": "published"
            }
        ]

        print(f"Inserting {len(opportunities_data)} new opportunities...")
        for data in opportunities_data:
            opp = Opportunity(
                owner_id=owner_id,
                title=data["title"],
                type=data["type"],
                description=data["description"],
                eligibility=data["eligibility"],
                sectors=json.dumps(data["sectors"]),
                target_stages=json.dumps(data["target_stages"]),
                countries=json.dumps(data["countries"]),
                deadline=data["deadline"],
                benefits=data["benefits"],
                status=data["status"]
            )
            db.session.add(opp)
        
        try:
            db.session.commit()
            print("Successfully seeded opportunities!")
        except Exception as e:
            print(f"Error seeding data: {e}")
            db.session.rollback()

if __name__ == "__main__":
    seed_opportunities()
