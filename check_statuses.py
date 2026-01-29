from app import create_app
from extensions import db
from models import Opportunity

app = create_app()
with app.app_context():
    opps = Opportunity.query.all()
    statuses = set(opp.status for opp in opps)
    print(f"Unique Statuses: {statuses}")
    for opp in opps:
        print(f"ID: {opp.id}, Status: '{opp.status}'")
