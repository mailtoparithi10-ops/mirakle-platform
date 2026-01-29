from app import create_app
from extensions import db
from models import Opportunity

app = create_app()
with app.app_context():
    opps = Opportunity.query.filter_by(status='published').all()
    for opp in opps:
        if not opp.title:
            print(f"ERROR: Opportunity ID {opp.id} has NO TITLE")
        else:
            print(f"ID {opp.id}: {opp.title[:20]}")
