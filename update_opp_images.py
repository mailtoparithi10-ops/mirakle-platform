
from app import create_app
from extensions import db
from models import Opportunity
import random

app = create_app()

images = [
    "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=2070&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1557804506-669a67965ba0?q=80&w=1974&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=2015&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?q=80&w=2070&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?q=80&w=2070&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1497366754035-f200968a6e72?q=80&w=2069&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1526628953301-3e589a6a8b74?q=80&w=2006&auto=format&fit=crop",
]

def update_images():
    with app.app_context():
        opps = Opportunity.query.all()
        print(f"Found {len(opps)} opportunities.")
        for opp in opps:
            if not opp.banner_url:
                opp.banner_url = random.choice(images)
                print(f"Updated {opp.title} with image.")
        
        db.session.commit()
        print("Done!")

if __name__ == "__main__":
    update_images()
