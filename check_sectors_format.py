from app import create_app
from extensions import db
from models import Opportunity
import json

app = create_app()
with app.app_context():
    opps = Opportunity.query.filter_by(status='published').all()
    for opp in opps:
        try:
            sectors = json.loads(opp.sectors or "[]")
            if not isinstance(sectors, list):
                print(f"ERROR: ID {opp.id} sectors is NOT A LIST: {type(sectors)}")
        except Exception as e:
            print(f"ERROR: ID {opp.id} sectors JSON LOAD FAILED: {e}")
