# enabler_service.py
"""
Enabler Service - Business logic for enabler dashboard
Handles referrals, rewards, analytics, and gamification
"""

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
    """Service class for enabler-related operations"""

    # ==========================================
    # REFERRAL MANAGEMENT
    # ==========================================

    @staticmethod
    def create_referral(enabler_id, opportunity_id, startup_name, startup_email, notes=None):
        """Create a new referral"""
        try:
            existing = Referral.query.filter_by(
                enabler_id=enabler_id,
                opportunity_id=opportunity_id,
                startup_email=startup_email
            ).first()
            
            if existing:
                return {"success": False, "message": "Referral already exists"}

            token = EnablerService._generate_referral_token()

            referral = Referral(
                enabler_id=enabler_id,
                opportunity_id=opportunity_id,
                startup_name=startup_name,
                startup_email=startup_email,
                token=token,
                is_link_referral=False,
                status="pending",
                notes=notes
            )

            db.session.add(referral)
            db.session.commit()

            EnablerService._ensure_enabler_level(enabler_id)

            return {
                "success": True,
                "referral": referral.to_dict(),
                "message": "Referral created successfully"
            }

        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    @staticmethod
    def generate_referral_link(enabler_id, opportunity_id):
        """Generate a unique referral link for an opportunity"""
        try:
            existing = Referral.query.filter_by(
                enabler_id=enabler_id,
                opportunity_id=opportunity_id,
                is_link_referral=True
            ).first()

            if existing:
                return {
                    "success": True,
                    "token": existing.token,
                    "link": f"/opportunities/{opportunity_id}?ref={existing.token}",
                    "message": "Using existing referral link"
                }

            token = EnablerService._generate_referral_token()
            opportunity = Opportunity.query.get(opportunity_id)
            if not opportunity:
                return {"success": False, "message": "Opportunity not found"}

            referral = Referral(
                enabler_id=enabler_id,
                opportunity_id=opportunity_id,
                startup_name="Link Referral",
                token=token,
                is_link_referral=True,
                status="active"
            )

            db.session.add(referral)
            db.session.commit()

            return {
                "success": True,
                "token": token,
                "link": f"/opportunities/{opportunity_id}?ref={token}",
                "referral_id": referral.id,
                "message": "Referral link generated successfully"
            }

        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    @staticmethod
    def track_referral_click(token, user_id=None, startup_id=None, ip_address=None, user_agent=None):
        """Track a click on a referral link"""
        try:
            referral = Referral.query.filter_by(token=token).first()
            if not referral:
                return {"success": False, "message": "Invalid referral token"}

            click = ReferralClick(
                referral_id=referral.id,
                user_id=user_id,
                startup_id=startup_id,
                ip_address=ip_address,
                user_agent=user_agent,
                viewed_opportunity=True
            )

            db.session.add(click)
            db.session.commit()

            return {
                "success": True,
                "referral_id": referral.id,
                "opportunity_id": referral.opportunity_id
            }

        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_enabler_referrals(enabler_id, status=None, limit=None):
        """Get all referrals for an enabler"""
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
                app = Application.query.filter_by(
                    startup_id=ref.startup_id,
                    opportunity_id=ref.opportunity_id
                ).first()
                if app:
                    ref_dict["application_status"] = app.status
            if ref.is_link_referral:
                clicks = ReferralClick.query.filter_by(referral_id=ref.id).count()
                conversions = ReferralClick.query.filter_by(
                    referral_id=ref.id,
                    applied=True
                ).count()
                ref_dict["clicks"] = clicks
                ref_dict["conversions"] = conversions
                ref_dict["conversion_rate"] = (conversions / clicks * 100) if clicks > 0 else 0
            result.append(ref_dict)

        return {"success": True, "referrals": result}

    @staticmethod
    def calculate_referral_reward(referral_id, reward_amount, reward_points=0):
        """Calculate and create reward for a successful referral"""
        try:
            referral = Referral.query.get(referral_id)
            if not referral:
                return {"success": False, "message": "Referral not found"}

            existing = RewardTransaction.query.filter_by(
                referral_id=referral_id,
                type="cash"
            ).first()

            if existing:
                return {"success": False, "message": "Reward already calculated"}

            opportunity = Opportunity.query.get(referral.opportunity_id)

            transaction = RewardTransaction(
                enabler_id=referral.enabler_id,
                referral_id=referral_id,
                type="cash",
                amount_money=reward_amount,
                amount_points=reward_points,
                status="pending",
                startup_name=referral.startup_name,
                program_name=opportunity.title if opportunity else "Unknown",
                description=f"Referral reward for {referral.startup_name}"
            )

            db.session.add(transaction)
            referral.status = "successful"

            level = EnablerLevel.query.filter_by(enabler_id=referral.enabler_id).first()
            if level:
                level.successful_referrals += 1
                level.points += reward_points
                level.total_earnings += reward_amount

            db.session.commit()
            EnablerService._update_daily_analytics(referral.enabler_id)

            return {
                "success": True,
                "transaction": transaction.to_dict(),
                "message": "Reward calculated successfully"
            }

        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_rewards_summary(enabler_id):
        """Get rewards summary for an enabler"""
        try:
            transactions = RewardTransaction.query.filter_by(enabler_id=enabler_id).all()

            available_balance = sum(
                t.amount_money for t in transactions
                if t.type in ["cash", "bonus"] and t.status == "settled"
            )

            pending_rewards = sum(
                t.amount_money for t in transactions
                if t.type in ["cash", "bonus"] and t.status == "pending"
            )

            payouts = sum(
                abs(t.amount_money) for t in transactions
                if t.type == "payout" and t.status == "paid"
            )

            available_balance -= payouts

            all_time_earnings = sum(
                t.amount_money for t in transactions
                if t.type in ["cash", "bonus"] and t.status in ["settled", "paid"]
            )

            total_points = sum(
                t.amount_points for t in transactions
                if t.type in ["cash", "points", "bonus"]
            )

            completed_rewards = [
                t for t in transactions
                if t.type == "cash" and t.status == "settled"
            ]
            avg_reward = (
                sum(t.amount_money for t in completed_rewards) / len(completed_rewards)
                if completed_rewards else 0
            )

            return {
                "success": True,
                "data": {
                    "available_balance": round(available_balance, 2),
                    "pending_rewards": round(pending_rewards, 2),
                    "all_time_earnings": round(all_time_earnings, 2),
                    "total_points": total_points,
                    "average_reward_per_completed_referral": round(avg_reward, 2)
                }
            }

        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_rewards_history(enabler_id, reward_type="all", page=1, per_page=10):
        """Get rewards transaction history"""
        try:
            query = RewardTransaction.query.filter_by(enabler_id=enabler_id)

            if reward_type != "all":
                if reward_type == "bonuses":
                    query = query.filter_by(type="bonus")
                else:
                    query = query.filter_by(type=reward_type)

            query = query.order_by(RewardTransaction.created_at.desc())
            total = query.count()
            transactions = query.offset((page - 1) * per_page).limit(per_page).all()

            return {
                "success": True,
                "data": {
                    "items": [t.to_dict() for t in transactions],
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total": total,
                        "total_pages": (total + per_page - 1) // per_page
                    }
                }
            }

        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def request_payout(enabler_id, amount, payout_method="bank_transfer"):
        """Request a payout"""
        try:
            summary = EnablerService.get_rewards_summary(enabler_id)
            if not summary["success"]:
                return summary

            available = summary["data"]["available_balance"]

            if amount > available:
                return {
                    "success": False,
                    "message": f"Insufficient balance. Available: ₹{available}"
                }

            if amount < 1000:
                return {
                    "success": False,
                    "message": "Minimum payout amount is ₹1,000"
                }

            transaction = RewardTransaction(
                enabler_id=enabler_id,
                type="payout",
                amount_money=-amount,
                status="pending",
                payout_method=payout_method,
                description=f"Payout request via {payout_method}"
            )

            db.session.add(transaction)
            db.session.commit()

            return {
                "success": True,
                "transaction": transaction.to_dict(),
                "message": "Payout request submitted successfully"
            }

        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_dashboard_overview(enabler_id, timeframe="30d"):
        """Get overview statistics for enabler dashboard"""
        try:
            if timeframe == "30d":
                start_date = datetime.utcnow() - timedelta(days=30)
            elif timeframe == "7d":
                start_date = datetime.utcnow() - timedelta(days=7)
            else:
                start_date = datetime(2020, 1, 1)

            referrals = Referral.query.filter(
                Referral.enabler_id == enabler_id,
                Referral.created_at >= start_date
            ).all()

            total_referrals = len(referrals)
            rewards = EnablerService.get_rewards_summary(enabler_id)
            confirmed_earnings = rewards["data"]["all_time_earnings"] if rewards["success"] else 0

            level = EnablerLevel.query.filter_by(enabler_id=enabler_id).first()
            flc_points = level.points if level else 0

            successful = len([r for r in referrals if r.status == "successful"])
            conversion_rate = (successful / total_referrals) if total_referrals > 0 else 0
            
            # Calculate unique startups and completed rewards
            unique_startups = len(set(r.startup_id for r in referrals if r.startup_id))
            completed_rewards = len([r for r in referrals if r.status == "successful"])

            recent_referrals = []
            for ref in referrals[:5]:
                opp = Opportunity.query.get(ref.opportunity_id)
                app_status = None

                if ref.startup_id:
                    app = Application.query.filter_by(
                        startup_id=ref.startup_id,
                        opportunity_id=ref.opportunity_id
                    ).first()
                    if app:
                        app_status = app.status

                recent_referrals.append({
                    "startup_name": ref.startup_name,
                    "program_name": opp.title if opp else "Unknown Program",
                    "status": ref.status,
                    "application_status": app_status,
                    "created_at": ref.created_at.isoformat(),
                    "reward": "₹2,500" if ref.status == "successful" else "Pending"
                })

            return {
                "success": True,
                "data": {
                    "summary": {
                        "total_referrals": total_referrals,
                        "confirmed_earnings": round(confirmed_earnings, 2),
                        "flc_points": flc_points,
                        "conversion_rate": round(conversion_rate, 2),
                        "unique_startups": unique_startups,
                        "completed_rewards": completed_rewards
                    },
                    "recent_referrals": recent_referrals
                }
            }

        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_analytics(enabler_id):
        """Get detailed analytics for enabler"""
        try:
            referrals = Referral.query.filter_by(enabler_id=enabler_id).all()

            submitted = len([r for r in referrals if r.status in ["pending", "accepted", "successful"]])
            shortlisted = len([r for r in referrals if r.status in ["accepted", "successful"]])
            completed = len([r for r in referrals if r.status == "successful"])

            conversion = (completed / submitted * 100) if submitted > 0 else 0

            unique_startups = len(set(r.startup_id for r in referrals if r.startup_id))
            avg_programs = submitted / unique_startups if unique_startups > 0 else 0

            sector_stats = {}
            for ref in referrals:
                opp = Opportunity.query.get(ref.opportunity_id)
                if opp and opp.sectors:
                    sectors = json.loads(opp.sectors)
                    for sector in sectors:
                        if sector not in sector_stats:
                            sector_stats[sector] = {"total": 0, "successful": 0}
                        sector_stats[sector]["total"] += 1
                        if ref.status == "successful":
                            sector_stats[sector]["successful"] += 1

            sectors = []
            for sector, stats in sector_stats.items():
                conversion_rate = (stats["successful"] / stats["total"] * 100) if stats["total"] > 0 else 0
                sectors.append({
                    "name": sector,
                    "conversion": round(conversion_rate, 1)
                })

            sectors.sort(key=lambda x: x["conversion"], reverse=True)

            return {
                "success": True,
                "data": {
                    "referral_stats": {
                        "submitted": submitted,
                        "shortlisted": shortlisted,
                        "completed": completed,
                        "conversion": round(conversion, 1),
                        "unique_startups": unique_startups,
                        "avg_programs_per_startup": round(avg_programs, 1),
                        "avg_decision_time": 21
                    },
                    "sectors": sectors[:5],
                    "signals": {
                        "emerging": "Climate & sustainability programs",
                        "best_days": "Tue–Thu",
                        "best_time": "10am–1pm IST"
                    }
                }
            }

        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_link_tracking_stats(enabler_id):
        """Get referral link tracking statistics"""
        try:
            link_referrals = Referral.query.filter_by(
                enabler_id=enabler_id,
                is_link_referral=True
            ).all()

            total_links = len(link_referrals)
            total_clicks = 0
            total_conversions = 0
            total_earnings = 0

            link_stats = []
            for ref in link_referrals:
                clicks = ReferralClick.query.filter_by(referral_id=ref.id).count()
                conversions = ReferralClick.query.filter_by(
                    referral_id=ref.id,
                    applied=True
                ).count()

                earnings = db.session.query(func.sum(RewardTransaction.amount_money)).filter(
                    RewardTransaction.referral_id == ref.id,
                    RewardTransaction.type == "cash",
                    RewardTransaction.status.in_(["settled", "paid"])
                ).scalar() or 0

                total_clicks += clicks
                total_conversions += conversions
                total_earnings += earnings

                opp = Opportunity.query.get(ref.opportunity_id)

                link_stats.append({
                    "referral_id": ref.id,
                    "token": ref.token,
                    "program_name": opp.title if opp else "Unknown",
                    "clicks": clicks,
                    "conversions": conversions,
                    "conversion_rate": round((conversions / clicks * 100) if clicks > 0 else 0, 1),
                    "earnings": round(earnings, 2),
                    "created_at": ref.created_at.isoformat()
                })

            link_stats.sort(key=lambda x: x["conversions"], reverse=True)

            return {
                "success": True,
                "data": {
                    "summary": {
                        "total_links": total_links,
                        "total_clicks": total_clicks,
                        "total_conversions": total_conversions,
                        "total_earnings": round(total_earnings, 2),
                        "avg_conversion_rate": round((total_conversions / total_clicks * 100) if total_clicks > 0 else 0, 1)
                    },
                    "links": link_stats
                }
            }

        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_enabler_level(enabler_id):
        """Get enabler level and gamification stats"""
        level = EnablerLevel.query.filter_by(enabler_id=enabler_id).first()

        if not level:
            level = EnablerLevel(enabler_id=enabler_id)
            db.session.add(level)
            db.session.commit()

        return {"success": True, "level": level.to_dict()}

    @staticmethod
    def update_enabler_level(enabler_id):
        """Update enabler level based on performance"""
        try:
            level = EnablerLevel.query.filter_by(enabler_id=enabler_id).first()
            if not level:
                level = EnablerLevel(enabler_id=enabler_id)
                db.session.add(level)

            referrals = Referral.query.filter_by(enabler_id=enabler_id).all()
            successful = len([r for r in referrals if r.status == "successful"])

            rewards = EnablerService.get_rewards_summary(enabler_id)
            earnings = rewards["data"]["all_time_earnings"] if rewards["success"] else 0

            level.total_referrals = len(referrals)
            level.successful_referrals = successful
            level.total_earnings = earnings
            level.points = successful * 100
            level.level = max(1, level.points // 500)

            if level.points < 1000:
                level.tier = "bronze"
            elif level.points < 2500:
                level.tier = "silver"
            elif level.points < 5000:
                level.tier = "gold"
            elif level.points < 10000:
                level.tier = "platinum"
            else:
                level.tier = "diamond"

            db.session.commit()

            return {"success": True, "level": level.to_dict()}

        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    @staticmethod
    def _generate_referral_token():
        """Generate a unique referral token"""
        while True:
            token = secrets.token_urlsafe(16)
            existing = Referral.query.filter_by(token=token).first()
            if not existing:
                return token

    @staticmethod
    def _ensure_enabler_level(enabler_id):
        """Ensure enabler level record exists"""
        level = EnablerLevel.query.filter_by(enabler_id=enabler_id).first()
        if not level:
            level = EnablerLevel(enabler_id=enabler_id)
            db.session.add(level)
            db.session.commit()

    @staticmethod
    def _update_daily_analytics(enabler_id):
        """Update daily analytics for an enabler"""
        try:
            today = date.today()

            analytics = EnablerAnalytics.query.filter_by(
                enabler_id=enabler_id,
                date=today
            ).first()

            if not analytics:
                analytics = EnablerAnalytics(
                    enabler_id=enabler_id,
                    date=today
                )
                db.session.add(analytics)

            referrals_today = Referral.query.filter(
                Referral.enabler_id == enabler_id,
                func.date(Referral.created_at) == today
            ).all()

            analytics.referrals_count = len(referrals_today)
            analytics.referrals_accepted = len([r for r in referrals_today if r.status == "accepted"])
            analytics.referrals_successful = len([r for r in referrals_today if r.status == "successful"])

            clicks_today = db.session.query(ReferralClick).join(Referral).filter(
                Referral.enabler_id == enabler_id,
                func.date(ReferralClick.clicked_at) == today
            ).count()

            conversions_today = db.session.query(ReferralClick).join(Referral).filter(
                Referral.enabler_id == enabler_id,
                func.date(ReferralClick.clicked_at) == today,
                ReferralClick.applied == True
            ).count()

            analytics.clicks_count = clicks_today
            analytics.conversions_count = conversions_today
            analytics.conversion_rate = (conversions_today / clicks_today * 100) if clicks_today > 0 else 0

            earnings_today = db.session.query(func.sum(RewardTransaction.amount_money)).filter(
                RewardTransaction.enabler_id == enabler_id,
                func.date(RewardTransaction.created_at) == today,
                RewardTransaction.type.in_(["cash", "bonus"]),
                RewardTransaction.status == "settled"
            ).scalar() or 0

            analytics.earnings_amount = earnings_today

            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print(f"Error updating analytics: {e}")

    @staticmethod
    def calculate_referral_reward(referral_id, reward_amount, reward_points=0):
        try:
            referral = Referral.query.get(referral_id)
            if not referral:
                return {"success": False, "message": "Referral not found"}
            existing = RewardTransaction.query.filter_by(referral_id=referral_id, type="cash").first()
            if existing:
                return {"success": False, "message": "Reward already calculated"}
            opportunity = Opportunity.query.get(referral.opportunity_id)
            transaction = RewardTransaction(enabler_id=referral.enabler_id, referral_id=referral_id, type="cash", amount_money=reward_amount, amount_points=reward_points, status="pending", startup_name=referral.startup_name, program_name=opportunity.title if opportunity else "Unknown", description=f"Referral reward for {referral.startup_name}")
            db.session.add(transaction)
            referral.status = "successful"
            level = EnablerLevel.query.filter_by(enabler_id=referral.enabler_id).first()
            if level:
                level.successful_referrals += 1
                level.points += reward_points
                level.total_earnings += reward_amount
            db.session.commit()
            EnablerService._update_daily_analytics(referral.enabler_id)
            return {"success": True, "transaction": transaction.to_dict(), "message": "Reward calculated successfully"}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def get_rewards_summary(enabler_id):
        try:
            transactions = RewardTransaction.query.filter_by(enabler_id=enabler_id).all()
            available_balance = sum(t.amount_money for t in transactions if t.type in ["cash", "bonus"] and t.status == "settled")
            pending_rewards = sum(t.amount_money for t in transactions if t.type in ["cash", "bonus"] and t.status == "pending")
            payouts = sum(abs(t.amount_money) for t in transactions if t.type == "payout" and t.status == "paid")
            available_balance -= payouts
            all_time_earnings = sum(t.amount_money for t in transactions if t.type in ["cash", "bonus"] and t.status in ["settled", "paid"])
            total_points = sum(t.amount_points for t in transactions if t.type in ["cash", "points", "bonus"])
            completed_rewards = [t for t in transactions if t.type == "cash" and t.status == "settled"]
            avg_reward = (sum(t.amount_money for t in completed_rewards) / len(completed_rewards)) if completed_rewards else 0
            return {"success": True, "data": {"available_balance": round(available_balance, 2), "pending_rewards": round(pending_rewards, 2), "all_time_earnings": round(all_time_earnings, 2), "total_points": total_points, "average_reward_per_completed_referral": round(avg_reward, 2)}}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def get_rewards_history(enabler_id, reward_type="all", page=1, per_page=10):
        try:
            query = RewardTransaction.query.filter_by(enabler_id=enabler_id)
            if reward_type != "all":
                if reward_type == "bonuses":
                    query = query.filter_by(type="bonus")
                else:
                    query = query.filter_by(type=reward_type)
            query = query.order_by(RewardTransaction.created_at.desc())
            total = query.count()
            transactions = query.offset((page - 1) * per_page).limit(per_page).all()
            return {"success": True, "data": {"items": [t.to_dict() for t in transactions], "pagination": {"page": page, "per_page": per_page, "total": total, "total_pages": (total + per_page - 1) // per_page}}}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def request_payout(enabler_id, amount, payout_method="bank_transfer"):
        try:
            summary = EnablerService.get_rewards_summary(enabler_id)
            if not summary["success"]:
                return summary
            available = summary["data"]["available_balance"]
            if amount > available:
                return {"success": False, "message": f"Insufficient balance. Available: ₹{available}"}
            if amount < 1000:
                return {"success": False, "message": "Minimum payout amount is ₹1,000"}
            transaction = RewardTransaction(enabler_id=enabler_id, type="payout", amount_money=-amount, status="pending", payout_method=payout_method, description=f"Payout request via {payout_method}")
            db.session.add(transaction)
            db.session.commit()
            return {"success": True, "transaction": transaction.to_dict(), "message": "Payout request submitted successfully"}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def get_dashboard_overview(enabler_id, timeframe="30d"):
        try:
            if timeframe == "30d":
                start_date = datetime.utcnow() - timedelta(days=30)
            elif timeframe == "7d":
                start_date = datetime.utcnow() - timedelta(days=7)
            else:
                start_date = datetime(2020, 1, 1)
            referrals = Referral.query.filter(Referral.enabler_id == enabler_id, Referral.created_at >= start_date).all()
            total_referrals = len(referrals)
            rewards = EnablerService.get_rewards_summary(enabler_id)
            confirmed_earnings = rewards["data"]["all_time_earnings"] if rewards["success"] else 0
            level = EnablerLevel.query.filter_by(enabler_id=enabler_id).first()
            flc_points = level.points if level else 0
            successful = len([r for r in referrals if r.status == "successful"])
            conversion_rate = (successful / total_referrals) if total_referrals > 0 else 0
            recent_referrals = []
            for ref in referrals[:5]:
                opp = Opportunity.query.get(ref.opportunity_id)
                app_status = None
                if ref.startup_id:
                    app = Application.query.filter_by(startup_id=ref.startup_id, opportunity_id=ref.opportunity_id).first()
                    if app:
                        app_status = app.status
                recent_referrals.append({"startup_name": ref.startup_name, "program_name": opp.title if opp else "Unknown Program", "status": ref.status, "application_status": app_status, "created_at": ref.created_at.isoformat(), "reward": "₹2,500" if ref.status == "successful" else "Pending"})
            return {"success": True, "data": {"summary": {"total_referrals": total_referrals, "confirmed_earnings": round(confirmed_earnings, 2), "flc_points": flc_points, "conversion_rate": round(conversion_rate, 2)}, "recent_referrals": recent_referrals}}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def get_analytics(enabler_id):
        try:
            referrals = Referral.query.filter_by(enabler_id=enabler_id).all()
            submitted = len([r for r in referrals if r.status in ["pending", "accepted", "successful"]])
            shortlisted = len([r for r in referrals if r.status in ["accepted", "successful"]])
            completed = len([r for r in referrals if r.status == "successful"])
            conversion = (completed / submitted * 100) if submitted > 0 else 0
            unique_startups = len(set(r.startup_id for r in referrals if r.startup_id))
            avg_programs = submitted / unique_startups if unique_startups > 0 else 0
            sector_stats = {}
            for ref in referrals:
                opp = Opportunity.query.get(ref.opportunity_id)
                if opp and opp.sectors:
                    sectors = json.loads(opp.sectors)
                    for sector in sectors:
                        if sector not in sector_stats:
                            sector_stats[sector] = {"total": 0, "successful": 0}
                        sector_stats[sector]["total"] += 1
                        if ref.status == "successful":
                            sector_stats[sector]["successful"] += 1
            sectors = []
            for sector, stats in sector_stats.items():
                conversion_rate = (stats["successful"] / stats["total"] * 100) if stats["total"] > 0 else 0
                sectors.append({"name": sector, "conversion": round(conversion_rate, 1)})
            sectors.sort(key=lambda x: x["conversion"], reverse=True)
            return {"success": True, "data": {"referral_stats": {"submitted": submitted, "shortlisted": shortlisted, "completed": completed, "conversion": round(conversion, 1), "unique_startups": unique_startups, "avg_programs_per_startup": round(avg_programs, 1), "avg_decision_time": 21}, "sectors": sectors[:5], "signals": {"emerging": "Climate & sustainability programs", "best_days": "Tue–Thu", "best_time": "10am–1pm IST"}}}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def get_link_tracking_stats(enabler_id):
        try:
            link_referrals = Referral.query.filter_by(enabler_id=enabler_id, is_link_referral=True).all()
            total_links = len(link_referrals)
            total_clicks = 0
            total_conversions = 0
            total_earnings = 0
            link_stats = []
            for ref in link_referrals:
                clicks = ReferralClick.query.filter_by(referral_id=ref.id).count()
                conversions = ReferralClick.query.filter_by(referral_id=ref.id, applied=True).count()
                earnings = db.session.query(func.sum(RewardTransaction.amount_money)).filter(RewardTransaction.referral_id == ref.id, RewardTransaction.type == "cash", RewardTransaction.status.in_(["settled", "paid"])).scalar() or 0
                total_clicks += clicks
                total_conversions += conversions
                total_earnings += earnings
                opp = Opportunity.query.get(ref.opportunity_id)
                link_stats.append({"referral_id": ref.id, "token": ref.token, "program_name": opp.title if opp else "Unknown", "clicks": clicks, "conversions": conversions, "conversion_rate": round((conversions / clicks * 100) if clicks > 0 else 0, 1), "earnings": round(earnings, 2), "created_at": ref.created_at.isoformat()})
            link_stats.sort(key=lambda x: x["conversions"], reverse=True)
            return {"success": True, "data": {"summary": {"total_links": total_links, "total_clicks": total_clicks, "total_conversions": total_conversions, "total_earnings": round(total_earnings, 2), "avg_conversion_rate": round((total_conversions / total_clicks * 100) if total_clicks > 0 else 0, 1)}, "links": link_stats}}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def get_enabler_level(enabler_id):
        level = EnablerLevel.query.filter_by(enabler_id=enabler_id).first()
        if not level:
            level = EnablerLevel(enabler_id=enabler_id)
            db.session.add(level)
            db.session.commit()
        return {"success": True, "level": level.to_dict()}
    
    @staticmethod
    def update_enabler_level(enabler_id):
        try:
            level = EnablerLevel.query.filter_by(enabler_id=enabler_id).first()
            if not level:
                level = EnablerLevel(enabler_id=enabler_id)
                db.session.add(level)
            referrals = Referral.query.filter_by(enabler_id=enabler_id).all()
            successful = len([r for r in referrals if r.status == "successful"])
            rewards = EnablerService.get_rewards_summary(enabler_id)
            earnings = rewards["data"]["all_time_earnings"] if rewards["success"] else 0
            level.total_referrals = len(referrals)
            level.successful_referrals = successful
            level.total_earnings = earnings
            level.points = successful * 100
            level.level = max(1, level.points // 500)
            if level.points < 1000:
                level.tier = "bronze"
            elif level.points < 2500:
                level.tier = "silver"
            elif level.points < 5000:
                level.tier = "gold"
            elif level.points < 10000:
                level.tier = "platinum"
            else:
                level.tier = "diamond"
            db.session.commit()
            return {"success": True, "level": level.to_dict()}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def _generate_referral_token():
        while True:
            token = secrets.token_urlsafe(16)
            existing = Referral.query.filter_by(token=token).first()
            if not existing:
                return token
    
    @staticmethod
    def _ensure_enabler_level(enabler_id):
        level = EnablerLevel.query.filter_by(enabler_id=enabler_id).first()
        if not level:
            level = EnablerLevel(enabler_id=enabler_id)
            db.session.add(level)
            db.session.commit()
    
    @staticmethod
    def _update_daily_analytics(enabler_id):
        try:
            today = date.today()
            analytics = EnablerAnalytics.query.filter_by(enabler_id=enabler_id, date=today).first()
            if not analytics:
                analytics = EnablerAnalytics(enabler_id=enabler_id, date=today)
                db.session.add(analytics)
            referrals_today = Referral.query.filter(Referral.enabler_id == enabler_id, func.date(Referral.created_at) == today).all()
            analytics.referrals_count = len(referrals_today)
            analytics.referrals_accepted = len([r for r in referrals_today if r.status == "accepted"])
            analytics.referrals_successful = len([r for r in referrals_today if r.status == "successful"])
            clicks_today = db.session.query(ReferralClick).join(Referral).filter(Referral.enabler_id == enabler_id, func.date(ReferralClick.clicked_at) == today).count()
            conversions_today = db.session.query(ReferralClick).join(Referral).filter(Referral.enabler_id == enabler_id, func.date(ReferralClick.clicked_at) == today, ReferralClick.applied == True).count()
            analytics.clicks_count = clicks_today
            analytics.conversions_count = conversions_today
            analytics.conversion_rate = (conversions_today / clicks_today * 100) if clicks_today > 0 else 0
            earnings_today = db.session.query(func.sum(RewardTransaction.amount_money)).filter(RewardTransaction.enabler_id == enabler_id, func.date(RewardTransaction.created_at) == today, RewardTransaction.type.in_(["cash", "bonus"]), RewardTransaction.status == "settled").scalar() or 0
            analytics.earnings_amount = earnings_today
            db.session.commit()
        except Exception as e:
            db.session.rollback()
