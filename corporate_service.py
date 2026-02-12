# corporate_service.py
from datetime import datetime, timedelta, date
from extensions import db
from models import (User, Startup, Opportunity, Application, StartupMatch, Deal, DealActivity, CorporateProfile, CorporateAnalytics)
from sqlalchemy import func, and_, or_, desc
import json
import secrets

class CorporateService:
    @staticmethod
    def get_dashboard_overview(corporate_id):
        try:
            profile = CorporateProfile.query.filter_by(user_id=corporate_id).first()
            total_startups = Startup.query.count()
            active_pilots = Deal.query.filter_by(corporate_id=corporate_id, stage='pilot', is_active=True).count()
            deal_flow_value = CorporateService.calculate_deal_flow_value(corporate_id)
            performance_analytics = CorporateService.get_performance_analytics(corporate_id, months=6)
            recent_matches = StartupMatch.query.filter_by(corporate_id=corporate_id).order_by(desc(StartupMatch.created_at)).limit(5).all()
            recent_applications = db.session.query(Application).join(Opportunity).filter(Opportunity.owner_id == corporate_id).order_by(desc(Application.created_at)).limit(5).all()
            return {"success": True, "total_startups": total_startups, "active_pilots": active_pilots, "deal_flow_value": f"${deal_flow_value:,.0f}", "performance_analytics": performance_analytics, "recent_matches": [m.to_dict() for m in recent_matches], "recent_applications": [a.to_dict() for a in recent_applications]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    @staticmethod
    def get_performance_analytics(corporate_id, months=6):
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)
        analytics = CorporateAnalytics.query.filter(and_(CorporateAnalytics.corporate_id == corporate_id, CorporateAnalytics.date >= start_date, CorporateAnalytics.date <= end_date)).order_by(CorporateAnalytics.date).all()
        monthly_data = {}
        for record in analytics:
            month_key = record.date.strftime("%b")
            if month_key not in monthly_data:
                monthly_data[month_key] = {"month": month_key, "startups_viewed": 0, "deals_created": 0}
            monthly_data[month_key]["startups_viewed"] += record.startups_viewed
            monthly_data[month_key]["deals_created"] += record.deals_created
        return list(monthly_data.values())
    @staticmethod
    def discover_startups(corporate_id, filters=None):
        try:
            profile = CorporateProfile.query.filter_by(user_id=corporate_id).first()
            query = Startup.query
            if filters:
                if filters.get('search'):
                    search_term = f"%{filters['search']}%"
                    query = query.filter(or_(Startup.name.ilike(search_term), Startup.description.ilike(search_term)))
                if filters.get('sector'):
                    query = query.filter(Startup.sectors.contains(filters['sector']))
                if filters.get('stage'):
                    query = query.filter_by(stage=filters['stage'])
            startups = query.limit(50).all()
            results = []
            for startup in startups:
                match_score = CorporateService.calculate_match_score(profile, startup)
                existing_match = StartupMatch.query.filter_by(corporate_id=corporate_id, startup_id=startup.id).first()
                if not existing_match and match_score > 50:
                    match = StartupMatch(corporate_id=corporate_id, startup_id=startup.id, match_score=match_score, match_factors=json.dumps({"sector": 0.4, "stage": 0.3, "location": 0.2, "funding": 0.1}), status='discovered')
                    db.session.add(match)
                startup_dict = startup.to_dict()
                startup_dict['match_score'] = match_score
                results.append(startup_dict)
            db.session.commit()
            results.sort(key=lambda x: x['match_score'], reverse=True)
            return {"success": True, "startups": results[:20], "total": len(results)}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}
    @staticmethod
    def calculate_match_score(corporate_profile, startup):
        score = 0.0
        if not corporate_profile:
            return 50
        if corporate_profile.innovation_focus:
            try:
                corp_sectors = json.loads(corporate_profile.innovation_focus) if isinstance(corporate_profile.innovation_focus, str) else corporate_profile.innovation_focus
                startup_sectors = json.loads(startup.sectors) if isinstance(startup.sectors, str) else []
                if corp_sectors and startup_sectors:
                    common_sectors = set(corp_sectors) & set(startup_sectors)
                    if common_sectors:
                        score += 40 * (len(common_sectors) / len(corp_sectors))
            except:
                pass
        if corporate_profile.preferred_stages:
            try:
                preferred_stages = json.loads(corporate_profile.preferred_stages) if isinstance(corporate_profile.preferred_stages, str) else corporate_profile.preferred_stages
                if startup.stage in preferred_stages:
                    score += 30
            except:
                pass
        if corporate_profile.investment_range_min and corporate_profile.investment_range_max:
            score += 15
        if startup.country:
            score += 10
        return min(100, max(0, score))
    @staticmethod
    def view_startup_profile(corporate_id, startup_id):
        try:
            match = StartupMatch.query.filter_by(corporate_id=corporate_id, startup_id=startup_id).first()
            if match:
                match.viewed_at = datetime.utcnow()
                if match.status == 'discovered':
                    match.status = 'viewed'
            else:
                startup = Startup.query.get(startup_id)
                profile = CorporateProfile.query.filter_by(user_id=corporate_id).first()
                match_score = CorporateService.calculate_match_score(profile, startup)
                match = StartupMatch(corporate_id=corporate_id, startup_id=startup_id, match_score=match_score, match_factors=json.dumps({}), status='viewed', viewed_at=datetime.utcnow())
                db.session.add(match)
            CorporateService.track_activity(corporate_id, 'startup_viewed')
            db.session.commit()
            return {"success": True, "viewed_at": match.viewed_at.isoformat()}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}
    @staticmethod
    def connect_with_startup(corporate_id, startup_id):
        try:
            match = StartupMatch.query.filter_by(corporate_id=corporate_id, startup_id=startup_id).first()
            if match:
                match.contacted_at = datetime.utcnow()
                match.status = 'contacted'
            CorporateService.track_activity(corporate_id, 'startup_contacted')
            db.session.commit()
            return {"success": True, "message": "Connection request sent"}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}
    @staticmethod
    def get_all_deals(corporate_id):
        try:
            deals = Deal.query.filter_by(corporate_id=corporate_id, is_active=True).order_by(Deal.created_at.desc()).all()
            deals_by_stage = {'new': [], 'contacted': [], 'dd': [], 'pilot': []}
            for deal in deals:
                if deal.stage in deals_by_stage:
                    deal_dict = deal.to_dict()
                    startup = Startup.query.get(deal.startup_id)
                    if startup:
                        deal_dict['startup'] = startup.to_dict()
                    deals_by_stage[deal.stage].append(deal_dict)
            counts = {k: len(v) for k, v in deals_by_stage.items()}
            return {"success": True, "deals": deals_by_stage, "counts": counts}
        except Exception as e:
            return {"success": False, "error": str(e)}
    @staticmethod
    def create_deal(corporate_id, startup_id, data):
        try:
            startup = Startup.query.get(startup_id)
            deal_name = data.get('name', f"Deal with {startup.name if startup else 'Startup'}")
            deal = Deal(corporate_id=corporate_id, startup_id=startup_id, name=deal_name, stage=data.get('stage', 'new'), value=data.get('value', 0.0), probability=data.get('probability', 50.0), notes=data.get('notes', ''), next_action=data.get('next_action'), next_action_date=data.get('next_action_date'), is_active=True)
            db.session.add(deal)
            db.session.flush()
            activity = DealActivity(deal_id=deal.id, activity_type='created', description=f"Deal created in {deal.stage} stage", created_by=corporate_id)
            db.session.add(activity)
            CorporateService.track_activity(corporate_id, 'deal_created')
            db.session.commit()
            return {"success": True, "deal": deal.to_dict()}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}
    @staticmethod
    def update_deal_stage(deal_id, new_stage, corporate_id):
        try:
            deal = Deal.query.get(deal_id)
            if not deal or deal.corporate_id != corporate_id:
                return {"success": False, "error": "Deal not found"}
            old_stage = deal.stage
            deal.stage = new_stage
            deal.updated_at = datetime.utcnow()
            activity = DealActivity(deal_id=deal_id, activity_type='stage_change', description=f"Moved from {old_stage} to {new_stage}", created_by=corporate_id)
            db.session.add(activity)
            CorporateService.track_activity(corporate_id, 'deal_moved')
            db.session.commit()
            return {"success": True, "deal": deal.to_dict()}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}
    @staticmethod
    def add_deal_note(deal_id, note, corporate_id):
        try:
            deal = Deal.query.get(deal_id)
            if not deal or deal.corporate_id != corporate_id:
                return {"success": False, "error": "Deal not found"}
            activity = DealActivity(deal_id=deal_id, activity_type='note', description=note, created_by=corporate_id)
            db.session.add(activity)
            db.session.commit()
            return {"success": True, "activity": activity.to_dict()}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}
    @staticmethod
    def calculate_deal_flow_value(corporate_id):
        result = db.session.query(func.sum(Deal.value)).filter_by(corporate_id=corporate_id, is_active=True).scalar()
        return result or 0.0
    @staticmethod
    def get_deal_details(deal_id, corporate_id):
        try:
            deal = Deal.query.get(deal_id)
            if not deal or deal.corporate_id != corporate_id:
                return {"success": False, "error": "Deal not found"}
            activities = DealActivity.query.filter_by(deal_id=deal_id).order_by(DealActivity.created_at.desc()).all()
            return {"success": True, "deal": deal.to_dict(), "activities": [a.to_dict() for a in activities]}
        except Exception as e:
            return {"success": False, "error": str(e)}
    @staticmethod
    def get_programs_with_engagement(corporate_id):
        try:
            programs = Opportunity.query.filter_by(owner_id=corporate_id).all()
            results = []
            for program in programs:
                program_dict = program.to_dict()
                applicant_count = Application.query.filter_by(opportunity_id=program.id).count()
                days_remaining = None
                if program.deadline:
                    delta = program.deadline - datetime.utcnow()
                    days_remaining = max(0, delta.days)
                program_dict['applicant_count'] = applicant_count
                program_dict['days_remaining'] = days_remaining
                program_dict['engagement_trend'] = 'High' if applicant_count > 20 else 'Moderate'
                results.append(program_dict)
            return {"success": True, "programs": results}
        except Exception as e:
            return {"success": False, "error": str(e)}
    @staticmethod
    def get_applications(corporate_id, filters=None):
        try:
            query = db.session.query(Application).join(Opportunity).filter(Opportunity.owner_id == corporate_id)
            if filters and filters.get('status'):
                query = query.filter(Application.status == filters['status'])
            applications = query.order_by(Application.created_at.desc()).all()
            results = []
            for app in applications:
                app_dict = app.to_dict()
                startup = Startup.query.get(app.startup_id)
                opportunity = Opportunity.query.get(app.opportunity_id)
                if startup:
                    app_dict['startup_name'] = startup.name
                if opportunity:
                    app_dict['opportunity_title'] = opportunity.title
                results.append(app_dict)
            return {"success": True, "applications": results, "total": len(results)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    @staticmethod
    def get_corporate_profile(corporate_id):
        try:
            profile = CorporateProfile.query.filter_by(user_id=corporate_id).first()
            if not profile:
                profile = CorporateProfile(user_id=corporate_id, innovation_focus=json.dumps([]), preferred_stages=json.dumps([]))
                db.session.add(profile)
                db.session.commit()
            return {"success": True, "profile": profile.to_dict()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    @staticmethod
    def update_corporate_profile(corporate_id, data):
        try:
            profile = CorporateProfile.query.filter_by(user_id=corporate_id).first()
            if not profile:
                profile = CorporateProfile(user_id=corporate_id)
                db.session.add(profile)
            if 'company_name' in data:
                profile.company_name = data['company_name']
            if 'industry' in data:
                profile.industry = data['industry']
            if 'company_size' in data:
                profile.company_size = data['company_size']
            if 'innovation_focus' in data:
                profile.innovation_focus = json.dumps(data['innovation_focus']) if isinstance(data['innovation_focus'], list) else data['innovation_focus']
            if 'investment_range_min' in data:
                profile.investment_range_min = data['investment_range_min']
            if 'investment_range_max' in data:
                profile.investment_range_max = data['investment_range_max']
            if 'preferred_stages' in data:
                profile.preferred_stages = json.dumps(data['preferred_stages']) if isinstance(data['preferred_stages'], list) else data['preferred_stages']
            db.session.commit()
            return {"success": True, "profile": profile.to_dict()}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}
    @staticmethod
    def track_activity(corporate_id, activity_type):
        try:
            today = date.today()
            analytics = CorporateAnalytics.query.filter_by(corporate_id=corporate_id, date=today).first()
            if not analytics:
                analytics = CorporateAnalytics(corporate_id=corporate_id, date=today)
                db.session.add(analytics)
            if activity_type == 'startup_viewed':
                analytics.startups_viewed += 1
            elif activity_type == 'startup_contacted':
                analytics.startups_contacted += 1
            elif activity_type == 'deal_created':
                analytics.deals_created += 1
            elif activity_type == 'deal_moved':
                analytics.deals_moved += 1
            db.session.commit()
        except Exception as e:
            db.session.rollback()
    @staticmethod
    def get_analytics(corporate_id, period='6m'):
        try:
            months = 6 if period == '6m' else 12
            end_date = date.today()
            start_date = end_date - timedelta(days=months * 30)
            analytics = CorporateAnalytics.query.filter(and_(CorporateAnalytics.corporate_id == corporate_id, CorporateAnalytics.date >= start_date, CorporateAnalytics.date <= end_date)).order_by(CorporateAnalytics.date).all()
            totals = {"startups_viewed": sum(a.startups_viewed for a in analytics), "startups_contacted": sum(a.startups_contacted for a in analytics), "deals_created": sum(a.deals_created for a in analytics), "applications_reviewed": sum(a.applications_reviewed for a in analytics)}
            monthly_data = {}
            for record in analytics:
                month_key = record.date.strftime("%Y-%m")
                if month_key not in monthly_data:
                    monthly_data[month_key] = {"month": record.date.strftime("%b %Y"), "startups_viewed": 0, "deals_created": 0, "applications_reviewed": 0}
                monthly_data[month_key]["startups_viewed"] += record.startups_viewed
                monthly_data[month_key]["deals_created"] += record.deals_created
                monthly_data[month_key]["applications_reviewed"] += record.applications_reviewed
            return {"success": True, "totals": totals, "monthly_data": list(monthly_data.values())}
        except Exception as e:
            return {"success": False, "error": str(e)}
