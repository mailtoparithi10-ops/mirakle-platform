# Admin Analytics Service
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from models import db, User, Opportunity, Application, Meeting, Referral, Lead
import csv, io

class AdminAnalyticsService:
    @staticmethod
    def get_user_growth_analytics(days=30):
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        daily_registrations = db.session.query(func.date(User.created_at).label('date'), func.count(User.id).label('count')).filter(User.created_at >= start_date).group_by(func.date(User.created_at)).order_by('date').all()
        role_growth = db.session.query(User.role, func.count(User.id).label('count')).filter(User.created_at >= start_date).group_by(User.role).all()
        total_by_role = db.session.query(User.role, func.count(User.id).label('count')).group_by(User.role).all()
        previous_period_start = start_date - timedelta(days=days)
        previous_count = User.query.filter(and_(User.created_at >= previous_period_start, User.created_at < start_date)).count()
        current_count = User.query.filter(User.created_at >= start_date).count()
        growth_rate = ((current_count - previous_count) / previous_count * 100) if previous_count > 0 else 0
        return {'daily_registrations': [{'date': str(r.date), 'count': r.count} for r in daily_registrations], 'role_growth': [{'role': r.role, 'count': r.count} for r in role_growth], 'total_by_role': [{'role': r.role, 'count': r.count} for r in total_by_role], 'growth_rate': round(growth_rate, 2), 'period_total': current_count, 'previous_period_total': previous_count}
    
    @staticmethod
    def get_application_funnel():
        total_startups = User.query.filter(or_(User.role == 'startup', User.role == 'founder')).count()
        startups_with_apps = db.session.query(func.count(func.distinct(Application.user_id))).scalar() or 0
        total_applications = Application.query.count()
        status_breakdown = db.session.query(Application.status, func.count(Application.id).label('count')).group_by(Application.status).all()
        accepted_count = Application.query.filter_by(status='accepted').count()
        conversion_rate = (startups_with_apps / total_startups * 100) if total_startups > 0 else 0
        acceptance_rate = (accepted_count / total_applications * 100) if total_applications > 0 else 0
        return {'total_startups': total_startups, 'startups_with_applications': startups_with_apps, 'conversion_rate': round(conversion_rate, 2), 'total_applications': total_applications, 'accepted_applications': accepted_count, 'acceptance_rate': round(acceptance_rate, 2), 'status_breakdown': [{'status': r.status, 'count': r.count} for r in status_breakdown]}
    
    @staticmethod
    def get_program_performance():
        top_programs = db.session.query(Opportunity.id, Opportunity.title, Opportunity.type, Opportunity.status, func.count(Application.id).label('application_count'), func.sum(func.case([(Application.status == 'accepted', 1)], else_=0)).label('accepted_count')).outerjoin(Application, Opportunity.id == Application.opportunity_id).group_by(Opportunity.id).order_by(func.count(Application.id).desc()).limit(10).all()
        type_distribution = db.session.query(Opportunity.type, func.count(Opportunity.id).label('count')).group_by(Opportunity.type).all()
        status_distribution = db.session.query(Opportunity.status, func.count(Opportunity.id).label('count')).group_by(Opportunity.status).all()
        return {'top_programs': [{'id': p.id, 'title': p.title, 'type': p.type, 'status': p.status, 'applications': p.application_count, 'accepted': p.accepted_count or 0, 'acceptance_rate': round((p.accepted_count or 0) / p.application_count * 100, 2) if p.application_count > 0 else 0} for p in top_programs], 'type_distribution': [{'type': t.type, 'count': t.count} for t in type_distribution], 'status_distribution': [{'status': s.status, 'count': s.count} for s in status_distribution]}
    
    @staticmethod
    def get_referral_analytics():
        total_referrals = Referral.query.count()
        successful_referrals = Referral.query.filter_by(status='successful').count()
        total_commissions = db.session.query(func.sum(Referral.commission_amount)).scalar() or 0
        top_enablers = db.session.query(User.id, User.name, User.email, func.count(Referral.id).label('referral_count'), func.sum(Referral.commission_amount).label('total_commission')).join(Referral, User.id == Referral.enabler_id).group_by(User.id).order_by(func.count(Referral.id).desc()).limit(10).all()
        status_breakdown = db.session.query(Referral.status, func.count(Referral.id).label('count')).group_by(Referral.status).all()
        conversion_rate = (successful_referrals / total_referrals * 100) if total_referrals > 0 else 0
        return {'total_referrals': total_referrals, 'successful_referrals': successful_referrals, 'conversion_rate': round(conversion_rate, 2), 'total_commissions': float(total_commissions), 'top_enablers': [{'id': e.id, 'name': e.name, 'email': e.email, 'referrals': e.referral_count, 'commission': float(e.total_commission or 0)} for e in top_enablers], 'status_breakdown': [{'status': s.status, 'count': s.count} for s in status_breakdown]}
    
    @staticmethod
    def get_meeting_analytics(days=30):
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        total_meetings = Meeting.query.filter(Meeting.created_at >= start_date).count()
        daily_meetings = db.session.query(func.date(Meeting.created_at).label('date'), func.count(Meeting.id).label('count')).filter(Meeting.created_at >= start_date).group_by(func.date(Meeting.created_at)).order_by('date').all()
        status_breakdown = db.session.query(Meeting.status, func.count(Meeting.id).label('count')).filter(Meeting.created_at >= start_date).group_by(Meeting.status).all()
        access_breakdown = db.session.query(Meeting.access_type, func.count(Meeting.id).label('count')).filter(Meeting.created_at >= start_date).group_by(Meeting.access_type).all()
        return {'total_meetings': total_meetings, 'avg_duration': 60, 'total_participants': total_meetings * 2, 'daily_meetings': [{'date': str(m.date), 'count': m.count} for m in daily_meetings], 'status_breakdown': [{'status': s.status, 'count': s.count} for s in status_breakdown], 'access_breakdown': [{'access_type': a.access_type, 'count': a.count} for a in access_breakdown]}
    
    @staticmethod
    def get_lead_analytics(days=30):
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        total_leads = Lead.query.filter(Lead.created_at >= start_date).count()
        read_leads = Lead.query.filter(and_(Lead.created_at >= start_date, Lead.is_read == True)).count()
        unread_leads = total_leads - read_leads
        type_breakdown = db.session.query(Lead.type, func.count(Lead.id).label('count')).filter(Lead.created_at >= start_date).group_by(Lead.type).all()
        daily_leads = db.session.query(func.date(Lead.created_at).label('date'), func.count(Lead.id).label('count')).filter(Lead.created_at >= start_date).group_by(func.date(Lead.created_at)).order_by('date').all()
        response_rate = (read_leads / total_leads * 100) if total_leads > 0 else 0
        return {'total_leads': total_leads, 'read_leads': read_leads, 'unread_leads': unread_leads, 'response_rate': round(response_rate, 2), 'type_breakdown': [{'type': t.type, 'count': t.count} for t in type_breakdown], 'daily_leads': [{'date': str(l.date), 'count': l.count} for l in daily_leads]}
    
    @staticmethod
    def get_platform_health():
        week_ago = datetime.utcnow() - timedelta(days=7)
        weekly_new_users = User.query.filter(User.created_at >= week_ago).count()
        weekly_new_applications = Application.query.filter(Application.created_at >= week_ago).count()
        weekly_new_meetings = Meeting.query.filter(Meeting.created_at >= week_ago).count()
        weekly_new_leads = Lead.query.filter(Lead.created_at >= week_ago).count()
        health_score = min((weekly_new_users * 2) + (weekly_new_applications * 3) + (weekly_new_meetings * 4) + (weekly_new_leads * 2), 100)
        two_weeks_ago = datetime.utcnow() - timedelta(days=14)
        previous_week_users = User.query.filter(and_(User.created_at >= two_weeks_ago, User.created_at < week_ago)).count()
        growth_rate = ((weekly_new_users - previous_week_users) / previous_week_users * 100) if previous_week_users > 0 else 0
        return {'health_score': health_score, 'weekly_new_users': weekly_new_users, 'weekly_new_applications': weekly_new_applications, 'weekly_new_meetings': weekly_new_meetings, 'weekly_new_leads': weekly_new_leads, 'user_growth_rate': round(growth_rate, 2)}
    
    @staticmethod
    def get_revenue_analytics(days=30):
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        total_revenue = db.session.query(func.sum(Referral.commission_amount)).filter(Referral.created_at >= start_date).scalar() or 0
        daily_revenue = db.session.query(func.date(Referral.created_at).label('date'), func.sum(Referral.commission_amount).label('revenue')).filter(Referral.created_at >= start_date).group_by(func.date(Referral.created_at)).order_by('date').all()
        top_earners = db.session.query(User.id, User.name, func.sum(Referral.commission_amount).label('total_revenue')).join(Referral, User.id == Referral.enabler_id).filter(Referral.created_at >= start_date).group_by(User.id).order_by(func.sum(Referral.commission_amount).desc()).limit(10).all()
        return {'total_revenue': float(total_revenue), 'daily_revenue': [{'date': str(r.date), 'revenue': float(r.revenue or 0)} for r in daily_revenue], 'top_earners': [{'id': e.id, 'name': e.name, 'revenue': float(e.total_revenue or 0)} for e in top_earners]}
    
    @staticmethod
    def get_comprehensive_report(days=30):
        return {'platform_health': AdminAnalyticsService.get_platform_health(), 'user_growth': AdminAnalyticsService.get_user_growth_analytics(days), 'application_funnel': AdminAnalyticsService.get_application_funnel(), 'program_performance': AdminAnalyticsService.get_program_performance(), 'referrals': AdminAnalyticsService.get_referral_analytics(), 'meetings': AdminAnalyticsService.get_meeting_analytics(days), 'leads': AdminAnalyticsService.get_lead_analytics(days), 'revenue': AdminAnalyticsService.get_revenue_analytics(days), 'generated_at': datetime.utcnow().isoformat()}
    
    @staticmethod
    def export_analytics_csv(analytics_type, days=30):
        output = io.StringIO()
        writer = csv.writer(output)
        if analytics_type == 'user_growth':
            data = AdminAnalyticsService.get_user_growth_analytics(days)
            writer.writerow(['Date', 'New Users'])
            for item in data['daily_registrations']:
                writer.writerow([item['date'], item['count']])
        elif analytics_type == 'applications':
            data = AdminAnalyticsService.get_application_funnel()
            writer.writerow(['Status', 'Count'])
            for item in data['status_breakdown']:
                writer.writerow([item['status'], item['count']])
        elif analytics_type == 'programs':
            data = AdminAnalyticsService.get_program_performance()
            writer.writerow(['Program', 'Type', 'Status', 'Applications', 'Accepted', 'Rate'])
            for item in data['top_programs']:
                writer.writerow([item['title'], item['type'], item['status'], item['applications'], item['accepted'], str(item['acceptance_rate']) + '%'])
        elif analytics_type == 'referrals':
            data = AdminAnalyticsService.get_referral_analytics()
            writer.writerow(['Enabler', 'Email', 'Referrals', 'Commission'])
            for item in data['top_enablers']:
                writer.writerow([item['name'], item['email'], item['referrals'], '$' + str(round(item['commission'], 2))])
        elif analytics_type == 'meetings':
            data = AdminAnalyticsService.get_meeting_analytics(days)
            writer.writerow(['Date', 'Meetings'])
            for item in data['daily_meetings']:
                writer.writerow([item['date'], item['count']])
        elif analytics_type == 'leads':
            data = AdminAnalyticsService.get_lead_analytics(days)
            writer.writerow(['Date', 'Leads'])
            for item in data['daily_leads']:
                writer.writerow([item['date'], item['count']])
        elif analytics_type == 'revenue':
            data = AdminAnalyticsService.get_revenue_analytics(days)
            writer.writerow(['Date', 'Revenue'])
            for item in data['daily_revenue']:
                writer.writerow([item['date'], '$' + str(round(item['revenue'], 2))])
        else:
            raise ValueError('Unknown analytics type: ' + analytics_type)
        return output.getvalue()
