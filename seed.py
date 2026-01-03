# seed.py
from app import create_app
from extensions import db
from models import User, Startup, Opportunity, Application, Referral
import json, datetime

app = create_app()

with app.app_context():
    # Optional: Uncomment to clear existing data (careful in production)
    # db.session.query(Referral).delete()
    # db.session.query(Application).delete()
    # db.session.query(Opportunity).delete()
    # db.session.query(Startup).delete()
    # db.session.query(User).delete()
    # db.session.commit()

    def add_user(name, email, role, country='India', company=None):
        existing = User.query.filter_by(email=email).first()
        if existing:
            return existing
        u = User(name=name, email=email, role=role, country=country, company=company)
        u.set_password('password123')
        db.session.add(u)
        db.session.flush()  # ensure id available
        return u

    # Create users
    admin = add_user('Admin User', 'admin@mirakle.local', 'admin', 'Global', 'Mirakle')
    f1 = add_user('Priya Founder', 'priya@startup.in', 'founder', 'India')
    f2 = add_user('John Founder', 'john@startup.us', 'founder', 'USA')
    conn = add_user('Asha Connector', 'asha@connector.org', 'connector', 'India', 'ConnectorOrg')
    corp = add_user('Acme Corp', 'acme@corp.com', 'corporate', 'USA', 'Acme Corp')
    inv = add_user('VC Europe', 'vc@europe.vc', 'corporate', 'UK', 'VentureEU')

    db.session.commit()

    # Create startups
    def add_startup(founder, name, website, country, sectors, stage, team_size, funding, problem, solution, traction, tags):
        s = Startup(
            founder_id=founder.id,
            name=name,
            website=website,
            country=country,
            sectors=json.dumps(sectors),
            stage=stage,
            team_size=team_size,
            funding=funding,
            problem=problem,
            solution=solution,
            traction=traction,
            pitch_deck_url='',
            demo_url='',
            tags=json.dumps(tags)
        )
        db.session.add(s)
        return s

    s1 = add_startup(f1, 'AgriTech India', 'https://agri.example', 'India', ['Agriculture','AI'], 'seed', '6-10', 'Pre-seed', 'Farm inefficiencies', 'IoT+AI for irrigation', 'Pilot with 3 farms', ['agri','india'])
    s2 = add_startup(f2, 'HealthNow', 'https://healthnow.example', 'USA', ['Health','SaaS'], 'series_a', '20-50', 'Series A', 'Patient scheduling pain', 'SaaS scheduling', '200 clinics onboarded', ['health','usa'])

    db.session.commit()

    # Create opportunities
    opp1 = Opportunity(
        owner_id=corp.id,
        title='Corporate PoC: Agri IoT',
        type='PoC',
        description='30k USD PoC for agri startups to pilot smart irrigation',
        eligibility='Seed to Series A',
        sectors=json.dumps(['Agriculture','IoT']),
        target_stages=json.dumps(['seed','series_a']),
        countries=json.dumps(['India']),
        deadline=(datetime.datetime.utcnow() + datetime.timedelta(days=30)),
        benefits='Pilot + commercial contract',
        status='published'
    )

    opp2 = Opportunity(
        owner_id=inv.id,
        title='EU Health Grant',
        type='grant',
        description='Grant for health innovations in EU markets',
        eligibility='All',
        sectors=json.dumps(['Health']),
        target_stages=json.dumps(['preseed','seed','series_a']),
        countries=json.dumps(['UK','Germany','France']),
        deadline=(datetime.datetime.utcnow() + datetime.timedelta(days=60)),
        benefits='Grant + mentorship',
        status='published'
    )

    db.session.add_all([opp1, opp2])
    db.session.commit()

    # Create an application (Priya applies to opp1)
    app1 = Application(
        startup_id=s1.id,
        opportunity_id=opp1.id,
        applied_by_id=f1.id,
        status='submitted',
        timeline=json.dumps([{'status':'submitted','note':'Initial submission','at':datetime.datetime.utcnow().isoformat(),'by':f1.id}]),
        notes=json.dumps(['Submitted via seed'])
    )
    db.session.add(app1)
    db.session.commit()

    # Create a referral (Connector refers AgriTech to opp1)
    ref1 = Referral(
        connector_id=conn.id,
        startup_id=s1.id,
        opportunity_id=opp1.id,
        status='open',
        reward_log=json.dumps([])
    )
    db.session.add(ref1)
    db.session.commit()

    print("Seeding complete. Users created:")
    for u in [admin, f1, f2, conn, corp, inv]:
        print(f" - {u.email} / password123 (role={u.role})")
