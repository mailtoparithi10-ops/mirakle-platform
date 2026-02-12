# enabler_service.py
from datetime import datetime, timedelta, date
from extensions import db
from models import (
    User, Referral, ReferralClick, Opportunity, Application, Startup,
    RewardTransaction, EnablerAnalytics, EnablerLevel
)
from sqlalchemy import func, and_, or_
import secrets
import json


class EnablerService:
    
    @staticmethod
    def create_referral(enabler_id, opportunity_id, startup_name, startup_email, notes=None):
        try:
            existing = Referral.query.filter_by(enabler_id=enabler_id, opportunity_id=opportunity_id, startup_email=startup_email).first()
            if existing:
                return {"success": False, "message": "Referral already exists"}
            token = EnablerService._generate_referral_token()
            referral = Referral(enabler_id=enabler_id, opportunity_id=opportunity_id, startup_name=startup_name, startup_email=startup_email, token=token, is_link_referral=False, status="pending", notes=notes)
            db.session.add(referral)
            db.session.commit()
            EnablerService._ensure_enabler_level(enabler_id)
            return {"success": True, "referral": referral.to_dict(), "message": "Referral created successfully"}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def generate_referral_link(enabler_id, opportunity_id):
        try:
            existing = Referral.query.filter_by(enabler_id=enabler_id, opportunity_id=opportunity_id, is_link_referral=True).first()
            if existing:
                return {"success": True, "token": existing.token, "link": f"/opportunities/{opportunity_id}?ref={existing.token}", "message": "Using existing referral link"}
            token = EnablerService._generate_referral_token()
            opportunity = Opportunity.query.get(opportunity_id)
            if not opportunity:
                return {"success": False, "message": "Opportunity not found"}
            referral = Referral(enabler_id=enabler_id, opportunity_id=opportunity_id, startup_name="Link Referral", token=token, is_link_referral=True, status="active")
            db.session.add(referral)
            db.session.commit()
            return {"success": True, "token": token, "link": f"/opportunities/{opportunity_id}?ref={token}", "referral_id": referral.id, "message": "Referral link generated successfully"}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def track_referral_click(token, user_id=None, startup_id=None, ip_address=None, user_agent=None):
        try:
            referral = Referral.query.filter_by(token=token).first()
            if not referral:
                return {"success": False, "message": "Invalid referral token"}
            click = ReferralClick(referral_id=referral.id, user_id=user_id, startup_id=startup_id, ip_address=ip_address, user_agent=user_agent, viewed_opportunity=True)
            db.session.add(click)
            db.session.commit()
            return {"success": True, "referral_id": referral.id, "opportunity_id": referral.opportunity_id}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def get_enabler_referrals(enabler_id, status=None, limit=None):
        query = Referral.query.filter_by(enabler_id=enabler_id)
        if status:
            query = query.filter_by(status=status)
        query = query.order_by(Referral.created_at.desc())
        if limit:
            query = query.limit(limit)
        referrals = query.all()
        result = []
        for ref in referrals:
            ref_dict = ref.to_dict()
            opp = Opportunity.query.get(ref.opportunity_id)
            if opp:
                ref_dict["program_name"] = opp.title
                ref_dict["program_type"] = opp.type
            if ref.startup_id:
                app = Application.query.filter_by(startup_id=ref.startup_id, opportunity_id=ref.opportunity_id).first()
                if app:
                    ref_dict["application_status"] = app.status
            if ref.is_link_referral:
                clicks = ReferralClick.query.filter_by(referral_id=ref.id).count()
                conversions = ReferralClick.query.filter_by(referral_id=ref.id, applied=True).count()
                ref_dict["clicks"] = clicks
                ref_dict["conversions"] = conversions
                ref_dict["conversion_rate"] = (conversions / clicks * 100) if clicks > 0 else 0
            result.append(ref_dict)
        return {"success": True, "referrals": result}
