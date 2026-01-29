from app import create_app
from extensions import db
from models import Opportunity

app = create_app()
with app.app_context():
    opps = Opportunity.query.all()
    print(f"Total Opportunities: {len(opps)}")
    published_count = 0
    for opp in opps:
        if opp.status == 'published':
            published_count += 1
        print(f"ID: {opp.id}, Title: {opp.title[:30]}, Status: {opp.status}")
    print(f"Total Published: {published_count}")
