"""
Admin Analytics Service
Provides comprehensive analytics and reporting for the admin dashboard
"""

from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from models import db, User, Opportunity, Application, Meeting, Referral, Lead
import csv
import io


class AdminAnalyticsService:
    """Service for generating admin analytics and reports"""

    @staticmethod
    def get_user_growth_analytics(days=30):
        """Get user growth analytics over specified period"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Daily user registrations
        daily_registrations = db.session.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).filter(
            User.created_at >= start_date
        ).group_by(
            func.date(User.created_at)
        ).order_by('date').all()

        # User growth by role
        role_growth = db.session.query(
            User.role,
            func.count(User.id).label('count')
        ).filter(
            User.created_at >= start_date
        ).group_by(User.role).all()

        # Total users by role (all time)
        total_by_role = db.session.query(
            User.role,
            func.count(User.id).label('count')
        ).group_by(User.role).all()

        # Calculate growth rate
        previous_period_start = start_date - timedelta(days=days)
        previous_count = User.query.filter(
            and_(User.created_at >= previous_period_start, User.created_at < start_date)
        ).count()
        current_count = User.query.filter(User.created_at >= start_date).count()
        
        growth_rate = 0
        if previous_count > 0:
            growth_rate = ((current_count - previous_count) / previous_count) * 100

        return {
            'daily_registrations': [
                {'date': str(r.date), 'count': r.count}
                for r in daily_registrations
            ],
            'role_growth': [
                {'role': r.role, 'count': r.count}
                for r in role_growth
            ],
            'total_by_role': [
                {'role': r.role, 'count': r.count}
                for r in total_by_role
            ],
            'growth_rate': round(growth_rate, 2),
            'period_total': current_count,
            'previous_period_total': previous_count
        }
