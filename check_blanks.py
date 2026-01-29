from app import create_app
from extensions import db
from models import Opportunity

app = create_app()
with app.app_context():
    opps = Opportunity.query.all()
    for opp in opps:
        if opp.sectors == "":
            print(f"ID {opp.id} has EMPTY STRING sectors")
        if opp.target_stages == "":
            print(f"ID {opp.id} has EMPTY STRING target_stages")
        if opp.countries == "":
            print(f"ID {opp.id} has EMPTY STRING countries")
