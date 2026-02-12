"""
Achievement Service
Handles achievement checking and awarding logic
"""

from extensions import db
from models import (
    Achievement, UserAchievement, User, Startup, Application,
    Referral, Connection, Message, Notification
)
from datetime import datetime, timedelta
import json


class AchievementService:
    """Service for checking and awarding achievements"""
    
    @staticmethod
    def check_and_award(user_id, achievement_code):
        """
        Check if user meets criteria for an achievement and award it
        
        Args:
            user_id: User ID
            achievement_code: Achievement code to check
            
        Returns:
            bool: True if awarded, False if already has it or doesn't meet criteria
        """
        user = User.query.get(user_id)
        if not user:
            return False
        
        # Check if user already has this achievement
        achievement = Achievement.query.filter_by(code=achievement_code, is_active=True).first()
        if not achievement:
            return False
        
        existing = UserAchievement.query.filter_by(
            user_id=user_id,
            achievement_id=achievement.id
        ).first()
        
        if existing:
            return False  # Already has it
        
        # Check criteria
        criteria = json.loads(achievement.criteria or '{}')
        criteria_type = criteria.get('type')
        criteria_value = criteria.get('value')
        
        meets_criteria = False
        
        if criteria_type == 'application_count':
            # Count applications
            if user.role == 'founder':
                startup = Startup.query.filter_by(founder_id=user_id).first()
                if startup:
                    count = Application.query.filter_by(startup_id=startup.id).count()
                    meets_criteria = count >= criteria_value
        
        elif criteria_type == 'application_speed':
            # Check if application was filed within X hours of signup
            if user.role == 'founder':
                startup = Startup.query.filter_by(founder_id=user_id).first()
                if startup:
                    first_app = Application.query.filter_by(startup_id=startup.id).order_by(Application.created_at.asc()).first()
                    if first_app:
                        time_diff = (first_app.created_at - user.created_at).total_seconds() / 3600
                        meets_criteria = time_diff <= criteria_value
        
        elif criteria_type == 'referral_count':
            # Count referrals received
            if user.role == 'founder':
                startup = Startup.query.filter_by(founder_id=user_id).first()
                if startup:
                    count = Referral.query.filter_by(startup_id=startup.id).count()
                    meets_criteria = count >= criteria_value
        
        elif criteria_type == 'connection_count':
            # Count accepted connections
            count = Connection.query.filter(
                Connection.status == 'accepted',
                db.or_(
                    Connection.requester_id == user_id,
                    Connection.recipient_id == user_id
                )
            ).count()
            meets_criteria = count >= criteria_value
        
        elif criteria_type == 'message_count':
            # Count messages sent
            count = Message.query.filter_by(sender_id=user_id).count()
            meets_criteria = count >= criteria_value
        
        elif criteria_type == 'profile_completion':
            # Check profile completion percentage
            if user.role == 'founder':
                startup = Startup.query.filter_by(founder_id=user_id).first()
                if startup:
                    completion = AchievementService._calculate_profile_completion(startup)
                    meets_criteria = completion >= criteria_value
        
        elif criteria_type == 'growth_score':
            # Check growth score
            if user.role == 'founder':
                from analytics_service import AnalyticsService
                startup = Startup.query.filter_by(founder_id=user_id).first()
                if startup:
                    score = AnalyticsService._calculate_growth_score(startup.id)
                    meets_criteria = score >= criteria_value
        
        elif criteria_type == 'funding_stage':
            # Check funding stage
            if user.role == 'founder':
                startup = Startup.query.filter_by(founder_id=user_id).first()
                if startup and startup.funding:
                    meets_criteria = criteria_value.lower() in startup.funding.lower()
        
        # Award achievement if criteria met
        if meets_criteria:
            user_achievement = UserAchievement(
                user_id=user_id,
                achievement_id=achievement.id,
                earned_at=datetime.utcnow(),
                progress=100
            )
            db.session.add(user_achievement)
            
            # Create notification
            notification = Notification(
                user_id=user_id,
                title='Achievement Unlocked! 🎉',
                message=f'You earned the "{achievement.name}" badge!',
                type='success',
                link='/startup/dashboard#achievements'
            )
            db.session.add(notification)
            
            # Track analytics
            from analytics_service import AnalyticsService
            AnalyticsService.track_event(
                event_type='achievement_earned',
                user_id=user_id,
                event_data={'achievement_code': achievement_code, 'achievement_name': achievement.name}
            )
            
            db.session.commit()
            return True
        
        return False
    
    @staticmethod
    def check_all_achievements(user_id):
        """Check all achievements for a user and award any that are earned"""
        achievements = Achievement.query.filter_by(is_active=True).all()
        awarded = []
        
        for achievement in achievements:
            if AchievementService.check_and_award(user_id, achievement.code):
                awarded.append(achievement.code)
        
        return awarded
    
    @staticmethod
    def check_all_users():
        """Check achievements for all users (run as cron job)"""
        users = User.query.filter_by(is_active=True).all()
        total_awarded = 0
        
        for user in users:
            awarded = AchievementService.check_all_achievements(user.id)
            total_awarded += len(awarded)
        
        return total_awarded
    
    @staticmethod
    def get_user_achievements(user_id):
        """Get all achievements for a user (earned and available)"""
        # Get all achievements
        all_achievements = Achievement.query.filter_by(is_active=True).all()
        
        # Get user's earned achievements
        earned_ids = [ua.achievement_id for ua in UserAchievement.query.filter_by(user_id=user_id).all()]
        
        earned = []
        locked = []
        
        for achievement in all_achievements:
            ach_dict = achievement.to_dict()
            
            if achievement.id in earned_ids:
                # Get earned date
                user_ach = UserAchievement.query.filter_by(
                    user_id=user_id,
                    achievement_id=achievement.id
                ).first()
                ach_dict['earned_at'] = user_ach.earned_at.isoformat() if user_ach else None
                ach_dict['progress'] = user_ach.progress if user_ach else 100
                earned.append(ach_dict)
            else:
                # Calculate progress for locked achievements
                progress = AchievementService._calculate_progress(user_id, achievement)
                ach_dict['progress'] = progress
                locked.append(ach_dict)
        
        return {
            'earned': earned,
            'locked': locked,
            'total_points': sum(a['points'] for a in earned)
        }
    
    @staticmethod
    def _calculate_progress(user_id, achievement):
        """Calculate progress percentage for an achievement"""
        criteria = json.loads(achievement.criteria or '{}')
        criteria_type = criteria.get('type')
        criteria_value = criteria.get('value', 1)
        
        user = User.query.get(user_id)
        if not user:
            return 0
        
        current_value = 0
        
        if criteria_type == 'application_count':
            if user.role == 'founder':
                startup = Startup.query.filter_by(founder_id=user_id).first()
                if startup:
                    current_value = Application.query.filter_by(startup_id=startup.id).count()
        
        elif criteria_type == 'referral_count':
            if user.role == 'founder':
                startup = Startup.query.filter_by(founder_id=user_id).first()
                if startup:
                    current_value = Referral.query.filter_by(startup_id=startup.id).count()
        
        elif criteria_type == 'connection_count':
            current_value = Connection.query.filter(
                Connection.status == 'accepted',
                db.or_(
                    Connection.requester_id == user_id,
                    Connection.recipient_id == user_id
                )
            ).count()
        
        elif criteria_type == 'message_count':
            current_value = Message.query.filter_by(sender_id=user_id).count()
        
        elif criteria_type == 'profile_completion':
            if user.role == 'founder':
                startup = Startup.query.filter_by(founder_id=user_id).first()
                if startup:
                    current_value = AchievementService._calculate_profile_completion(startup)
        
        elif criteria_type == 'growth_score':
            if user.role == 'founder':
                from analytics_service import AnalyticsService
                startup = Startup.query.filter_by(founder_id=user_id).first()
                if startup:
                    current_value = AnalyticsService._calculate_growth_score(startup.id)
        
        # Calculate percentage
        try:
            criteria_value_num = float(criteria_value) if criteria_value else 1
            if criteria_value_num > 0:
                progress = min(int((current_value / criteria_value_num) * 100), 100)
            else:
                progress = 0
        except (ValueError, TypeError):
            # If criteria_value is not numeric (e.g., 'series_a'), return 0 or 100
            progress = 100 if current_value else 0
        
        return progress
    
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
    def trigger_achievement_check(user_id, event_type):
        """
        Trigger achievement check based on specific events
        
        Args:
            user_id: User ID
            event_type: Type of event that occurred
        """
        # Map events to relevant achievements
        event_achievement_map = {
            'application_filed': ['early_mover', 'speed_demon'],
            'referral_received': ['enabler_approved'],
            'connection_made': ['networker'],
            'message_sent': ['communicator'],
            'profile_updated': ['profile_complete'],
            'funding_updated': ['funded_master'],
            'growth_score_updated': ['ecosystem_leader']
        }
        
        achievements_to_check = event_achievement_map.get(event_type, [])
        
        for achievement_code in achievements_to_check:
            AchievementService.check_and_award(user_id, achievement_code)
