from app import create_app
from extensions import db
from models import Opportunity
import json

app = create_app()
with app.app_context():
    opps = Opportunity.query.filter_by(status='published').all()
    print(f"Checking {len(opps)} opportunities...")
    for opp in opps:
        try:
            json.loads(opp.sectors or "[]")
            json.loads(opp.target_stages or "[]")
            json.loads(opp.countries or "[]")
        except Exception as e:
            print(f"FAILED on ID {opp.id}: {e}")
    print("Done.")
