"""
Analytics Service
Handles event tracking and metrics calculation for real-time analytics
"""

from extensions import db
from models import (
    AnalyticsEvent, StartupMetrics, Startup, Application, 
    Referral, ReferralClick, Connection, Message
)
from datetime import datetime, timedelta, date
import json
from sqlalchemy import func


class AnalyticsService:
    """Service for tracking analytics events and calculating metrics"""
    
    @staticmethod
    def track_event(event_type, user_id=None, startup_id=None, event_data=None, metadata=None):
        """
        Track an analytics event
        
        Args:
            event_type: Type of event (profile_view, application_filed, etc.)
            user_id: User ID (optional)
            startup_id: Startup ID (optional)
            event_data: Event-specific data (dict)
            metadata: Additional metadata (dict)
        """
        try:
            event = AnalyticsEvent(
                user_id=user_id,
                startup_id=startup_id,
                event_type=event_type,
                event_data=json.dumps(event_data or {}),
                event_metadata=json.dumps(metadata or {})
            )
            db.session.add(event)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error tracking event: {e}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_startup_analytics(startup_id, days=180):
        """
        Get comprehensive analytics for a startup
        
        Returns:
            dict: Analytics data including funnel, growth, and radar metrics
        """
        startup = Startup.query.get(startup_id)
        if not startup:
            return None
        
        # Get date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # 1. FUNNEL DATA (Real data)
        # Profile views from analytics events
        profile_views = AnalyticsEvent.query.filter(
            AnalyticsEvent.startup_id == startup_id,
            AnalyticsEvent.event_type == 'profile_view',
            AnalyticsEvent.created_at >= start_date
        ).count()
        
        # Referral clicks
        referral_clicks = db.session.query(func.count(ReferralClick.id)).join(
            Referral, ReferralClick.referral_id == Referral.id
        ).filter(
            Referral.startup_id == startup_id,
            ReferralClick.clicked_at >= start_date
        ).scalar() or 0
        
        # Referrals received
        referrals_received = Referral.query.filter(
            Referral.startup_id == startup_id,
            Referral.created_at >= start_date
        ).count()
        
        # Applications filed
        applications_filed = Application.query.filter(
            Application.startup_id == startup_id,
            Application.created_at >= start_date
        ).count()
        
        # Applications selected
        applications_selected = Application.query.filter(
            Application.startup_id == startup_id,
            Application.status == 'selected',
            Application.created_at >= start_date
        ).count()
        
        funnel_data = {
            'labels': ['Discovery', 'Referrals', 'Applications', 'Selected'],
            'data': [
                max(profile_views, referral_clicks, 10),  # Discovery
                referrals_received,
                applications_filed,
                applications_selected
            ]
        }
        
        # 2. GROWTH SCORE (Historical - last 6 months)
        growth_history = AnalyticsService._calculate_growth_history(startup_id, months=6)
        
        # 3. ECOSYSTEM FIT (Radar Chart)
        radar_data = AnalyticsService._calculate_ecosystem_fit(startup)
        
        return {
            'success': True,
            'funnel': funnel_data,
            'growth': growth_history,
            'radar': radar_data,
            'summary': {
                'profile_views': profile_views,
                'referrals_received': referrals_received,
                'applications_filed': applications_filed,
                'applications_selected': applications_selected,
                'conversion_rate': round((applications_selected / applications_filed * 100) if applications_filed > 0 else 0, 1)
            }
        }
    
    @staticmethod
    def _calculate_growth_history(startup_id, months=6):
        """Calculate growth score history for the last N months"""
        startup = Startup.query.get(startup_id)
        if not startup:
            return {'labels': [], 'data': []}
        
        # Get monthly snapshots or calculate on the fly
        end_date = date.today()
        labels = []
        scores = []
        
        for i in range(months, 0, -1):
            month_date = end_date - timedelta(days=30 * i)
            labels.append(month_date.strftime('%b'))
            
            # Check if we have a snapshot for this month
            snapshot = StartupMetrics.query.filter(
                StartupMetrics.startup_id == startup_id,
                func.extract('year', StartupMetrics.snapshot_date) == month_date.year,
                func.extract('month', StartupMetrics.snapshot_date) == month_date.month
            ).first()
            
            if snapshot:
                scores.append(snapshot.growth_score)
            else:
                # Calculate score for this period
                score = AnalyticsService._calculate_growth_score(startup_id, month_date)
                scores.append(score)
        
        return {
            'labels': labels,
            'data': scores
        }
    
    @staticmethod
    def _calculate_growth_score(startup_id, as_of_date=None):
        """Calculate growth score for a startup at a specific date"""
        if as_of_date is None:
            as_of_date = date.today()
        
        startup = Startup.query.get(startup_id)
        if not startup:
            return 60
        
        # Base score
        score = 60
        
        # Application status bonus
        if startup.application_status == 'submitted':
            score += 15
        elif startup.application_status == 'approved':
            score += 25
        
        # Referrals bonus (up to 20 points)
        referrals_count = Referral.query.filter(
            Referral.startup_id == startup_id,
            Referral.created_at <= as_of_date
        ).count()
        score += min(referrals_count * 5, 20)
        
        # Applications bonus (up to 15 points)
        applications_count = Application.query.filter(
            Application.startup_id == startup_id,
            Application.created_at <= as_of_date
        ).count()
        score += min(applications_count * 3, 15)
        
        # Connections bonus (up to 10 points)
        connections_count = Connection.query.filter(
            Connection.status == 'accepted',
            db.or_(
                Connection.requester_id == startup.founder_id,
                Connection.recipient_id == startup.founder_id
            ),
            Connection.created_at <= as_of_date
        ).count()
        score += min(connections_count * 2, 10)
        
        # Profile completion bonus (up to 10 points)
        completion = AnalyticsService._calculate_profile_completion(startup)
        score += int(completion / 10)
        
        return min(score, 100)  # Cap at 100
    
    @staticmethod
    def _calculate_ecosystem_fit(startup):
        """Calculate ecosystem fit scores for radar chart"""
        sectors_count = len(json.loads(startup.sectors or '[]'))
        
        # Tech Score (based on sectors and innovation)
        tech_score = 70 + (min(sectors_count, 3) * 10)
        
        # Market Score (based on stage and traction)
        if startup.stage in ('seed', 'series_a'):
            market_score = 85
        elif startup.stage in ('pre_seed', 'idea'):
            market_score = 65
        else:
            market_score = 75
        
        # Team Score (based on team size and info)
        team_score = 60
        if startup.team_size:
            try:
                size = int(startup.team_size.split('-')[0] if '-' in startup.team_size else startup.team_size)
                if size >= 5:
                    team_score = 85
                elif size >= 3:
                    team_score = 75
            except:
                pass
        if startup.team_info and len(startup.team_info) > 100:
            team_score += 10
        
        # Capital Score (based on funding and financials)
        capital_score = 60
        if startup.funding:
            if 'series' in startup.funding.lower():
                capital_score = 90
            elif 'seed' in startup.funding.lower():
                capital_score = 75
        if startup.financials and len(startup.financials) > 100:
            capital_score += 10
        
        # Product Score (based on description, demo, traction)
        product_score = 70
        if startup.demo_url:
            product_score += 10
        if startup.traction and len(startup.traction) > 100:
            product_score += 15
        
        return {
            'labels': ['Tech', 'Market', 'Team', 'Capital', 'Product'],
            'values': [
                min(tech_score, 100),
                min(market_score, 100),
                min(team_score, 100),
                min(capital_score, 100),
                min(product_score, 100)
            ]
        }
    
    @staticmethod
    def _calculate_profile_completion(startup):
        """Calculate profile completion percentage"""
        fields = [
            startup.name, startup.website, startup.linkedin, startup.location,
            startup.sectors, startup.stage, startup.team_size, startup.funding,
            startup.description, startup.problem, startup.solution, startup.traction,
            startup.business_model, startup.team_info, startup.pitch_deck_url, startup.logo_url
        ]
        
        completed = sum(1 for field in fields if field)
        return int((completed / len(fields)) * 100)
    
    @staticmethod
    def create_daily_snapshot(startup_id):
        """Create a daily metrics snapshot for a startup"""
        startup = Startup.query.get(startup_id)
        if not startup:
            return False
        
        today = date.today()
        
        # Check if snapshot already exists for today
        existing = StartupMetrics.query.filter(
            StartupMetrics.startup_id == startup_id,
            StartupMetrics.snapshot_date == today
        ).first()
        
        if existing:
            return False  # Already created today
        
        # Calculate metrics
        profile_views = AnalyticsEvent.query.filter(
            AnalyticsEvent.startup_id == startup_id,
            AnalyticsEvent.event_type == 'profile_view',
            func.date(AnalyticsEvent.created_at) == today
        ).count()
        
        referrals_received = Referral.query.filter(
            Referral.startup_id == startup_id,
            func.date(Referral.created_at) == today
        ).count()
        
        applications_filed = Application.query.filter(
            Application.startup_id == startup_id,
            func.date(Application.created_at) == today
        ).count()
        
        applications_selected = Application.query.filter(
            Application.startup_id == startup_id,
            Application.status == 'selected',
            func.date(Application.created_at) == today
        ).count()
        
        # Messages
        messages_sent = Message.query.filter(
            Message.sender_id == startup.founder_id,
            func.date(Message.created_at) == today
        ).count()
        
        messages_received = Message.query.filter(
            Message.recipient_id == startup.founder_id,
            func.date(Message.created_at) == today
        ).count()
        
        # Connections
        connections_made = Connection.query.filter(
            Connection.status == 'accepted',
            db.or_(
                Connection.requester_id == startup.founder_id,
                Connection.recipient_id == startup.founder_id
            ),
            func.date(Connection.accepted_at) == today
        ).count()
        
        # Calculate scores
        growth_score = AnalyticsService._calculate_growth_score(startup_id, today)
        radar_data = AnalyticsService._calculate_ecosystem_fit(startup)
        
        # Create snapshot
        snapshot = StartupMetrics(
            startup_id=startup_id,
            snapshot_date=today,
            profile_views=profile_views,
            referrals_received=referrals_received,
            applications_filed=applications_filed,
            applications_selected=applications_selected,
            messages_sent=messages_sent,
            messages_received=messages_received,
            connections_made=connections_made,
            growth_score=growth_score,
            tech_score=radar_data['values'][0],
            market_score=radar_data['values'][1],
            team_score=radar_data['values'][2],
            capital_score=radar_data['values'][3],
            product_score=radar_data['values'][4]
        )
        
        db.session.add(snapshot)
        db.session.commit()
        
        return True
    
    @staticmethod
    def create_snapshots_for_all_startups():
        """Create daily snapshots for all startups (run as cron job)"""
        startups = Startup.query.all()
        created_count = 0
        
        for startup in startups:
            if AnalyticsService.create_daily_snapshot(startup.id):
                created_count += 1
        
        return created_count
