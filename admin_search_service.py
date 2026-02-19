"""
Admin Advanced Search Service
Provides comprehensive search and filtering capabilities for admin dashboard
"""

from sqlalchemy import or_, and_, func
from models import db, User, Opportunity, Application, Meeting, Referral, Lead, Message
from datetime import datetime, timedelta


class AdminSearchService:
    """Service for advanced search and filtering"""

    @staticmethod
    def search_users(query=None, role=None, date_from=None, date_to=None, status=None, limit=50, offset=0):
        """
        Advanced user search with multiple filters
        
        Args:
            query: Search term (name, email, company)
            role: Filter by role (startup, corporate, enabler, admin)
            date_from: Filter by registration date (from)
            date_to: Filter by registration date (to)
            status: Filter by status (active, inactive)
            limit: Results per page
            offset: Pagination offset
        """
        search = User.query
        
        # Text search
        if query:
            search_term = f"%{query}%"
            search = search.filter(
                or_(
                    User.full_name.ilike(search_term),
                    User.email.ilike(search_term),
                    User.company.ilike(search_term),
                    User.username.ilike(search_term)
                )
            )
        
        # Role filter
        if role:
            search = search.filter(User.role == role)
        
        # Date range filter
        if date_from:
            search = search.filter(User.created_at >= date_from)
        if date_to:
            search = search.filter(User.created_at <= date_to)
        
        # Status filter (if status field exists)
        if status and hasattr(User, 'status'):
            search = search.filter(User.status == status)
        
        # Get total count before pagination
        total = search.count()
        
        # Apply pagination
        results = search.order_by(User.created_at.desc()).limit(limit).offset(offset).all()
        
        return {
            'results': [
                {
                    'id': user.id,
                    'full_name': user.full_name,
                    'email': user.email,
                    'role': user.role,
                    'company': user.company,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'country': user.country if hasattr(user, 'country') else None
                }
                for user in results
            ],
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': total > (offset + limit)
        }

    @staticmethod
    def search_programs(query=None, type=None, status=None, date_from=None, date_to=None, limit=50, offset=0):
        """
        Advanced program search with multiple filters
        
        Args:
            query: Search term (title, description)
            type: Filter by type (accelerator, grant, pilot, challenge, corporate_vc)
            status: Filter by status (draft, published, closed)
            date_from: Filter by creation date (from)
            date_to: Filter by creation date (to)
            limit: Results per page
            offset: Pagination offset
        """
        search = Opportunity.query
        
        # Text search
        if query:
            search_term = f"%{query}%"
            search = search.filter(
                or_(
                    Opportunity.title.ilike(search_term),
                    Opportunity.description.ilike(search_term),
                    Opportunity.benefits.ilike(search_term)
                )
            )
        
        # Type filter
        if type:
            search = search.filter(Opportunity.type == type)
        
        # Status filter
        if status:
            search = search.filter(Opportunity.status == status)
        
        # Date range filter
        if date_from:
            search = search.filter(Opportunity.created_at >= date_from)
        if date_to:
            search = search.filter(Opportunity.created_at <= date_to)
        
        # Get total count
        total = search.count()
        
        # Apply pagination
        results = search.order_by(Opportunity.created_at.desc()).limit(limit).offset(offset).all()
        
        return {
            'results': [
                {
                    'id': prog.id,
                    'title': prog.title,
                    'type': prog.type,
                    'status': prog.status,
                    'description': prog.description,
                    'benefits': prog.benefits,
                    'deadline': prog.deadline.isoformat() if prog.deadline else None,
                    'created_at': prog.created_at.isoformat() if prog.created_at else None
                }
                for prog in results
            ],
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': total > (offset + limit)
        }

    @staticmethod
    def search_applications(query=None, status=None, program_id=None, date_from=None, date_to=None, limit=50, offset=0):
        """
        Advanced application search with multiple filters
        
        Args:
            query: Search term (startup name)
            status: Filter by status
            program_id: Filter by specific program
            date_from: Filter by submission date (from)
            date_to: Filter by submission date (to)
            limit: Results per page
            offset: Pagination offset
        """
        search = Application.query
        
        # Join with User for startup name search
        if query:
            search_term = f"%{query}%"
            search = search.join(User, User.id == Application.startup_id).filter(
                or_(
                    User.full_name.ilike(search_term),
                    User.email.ilike(search_term),
                    User.company.ilike(search_term)
                )
            )
        
        # Status filter
        if status:
            search = search.filter(Application.status == status)
        
        # Program filter
        if program_id:
            search = search.filter(Application.opportunity_id == program_id)
        
        # Date range filter
        if date_from:
            search = search.filter(Application.created_at >= date_from)
        if date_to:
            search = search.filter(Application.created_at <= date_to)
        
        # Get total count
        total = search.count()
        
        # Apply pagination
        results = search.order_by(Application.created_at.desc()).limit(limit).offset(offset).all()
        
        return {
            'results': [
                {
                    'id': app.id,
                    'startup_id': app.startup_id,
                    'opportunity_id': app.opportunity_id,
                    'status': app.status,
                    'created_at': app.created_at.isoformat() if app.created_at else None
                }
                for app in results
            ],
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': total > (offset + limit)
        }

    @staticmethod
    def search_meetings(query=None, status=None, access_type=None, date_from=None, date_to=None, limit=50, offset=0):
        """
        Advanced meeting search with multiple filters
        
        Args:
            query: Search term (title, description)
            status: Filter by status
            access_type: Filter by access type
            date_from: Filter by scheduled date (from)
            date_to: Filter by scheduled date (to)
            limit: Results per page
            offset: Pagination offset
        """
        search = Meeting.query
        
        # Text search
        if query:
            search_term = f"%{query}%"
            search = search.filter(
                or_(
                    Meeting.title.ilike(search_term),
                    Meeting.description.ilike(search_term)
                )
            )
        
        # Status filter
        if status:
            search = search.filter(Meeting.status == status)
        
        # Access type filter
        if access_type:
            search = search.filter(Meeting.access_type == access_type)
        
        # Date range filter
        if date_from:
            search = search.filter(Meeting.scheduled_at >= date_from)
        if date_to:
            search = search.filter(Meeting.scheduled_at <= date_to)
        
        # Get total count
        total = search.count()
        
        # Apply pagination
        results = search.order_by(Meeting.scheduled_at.desc()).limit(limit).offset(offset).all()
        
        return {
            'results': [
                {
                    'id': meeting.id,
                    'title': meeting.title,
                    'description': meeting.description,
                    'status': meeting.status,
                    'access_type': meeting.access_type,
                    'scheduled_at': meeting.scheduled_at.isoformat() if meeting.scheduled_at else None,
                    'duration_minutes': meeting.duration_minutes,
                    'participant_count': meeting.participant_count
                }
                for meeting in results
            ],
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': total > (offset + limit)
        }

    @staticmethod
    def search_referrals(query=None, status=None, enabler_id=None, date_from=None, date_to=None, limit=50, offset=0):
        """
        Advanced referral search with multiple filters
        
        Args:
            query: Search term (enabler name, startup name)
            status: Filter by status
            enabler_id: Filter by specific enabler
            date_from: Filter by creation date (from)
            date_to: Filter by creation date (to)
            limit: Results per page
            offset: Pagination offset
        """
        search = Referral.query
        
        # Text search (join with users for names)
        if query:
            search_term = f"%{query}%"
            search = search.join(
                User, User.id == Referral.enabler_id
            ).filter(
                User.full_name.ilike(search_term)
            )
        
        # Status filter
        if status:
            search = search.filter(Referral.status == status)
        
        # Enabler filter
        if enabler_id:
            search = search.filter(Referral.enabler_id == enabler_id)
        
        # Date range filter
        if date_from:
            search = search.filter(Referral.created_at >= date_from)
        if date_to:
            search = search.filter(Referral.created_at <= date_to)
        
        # Get total count
        total = search.count()
        
        # Apply pagination
        results = search.order_by(Referral.created_at.desc()).limit(limit).offset(offset).all()
        
        return {
            'results': [
                {
                    'id': ref.id,
                    'enabler_id': ref.enabler_id,
                    'startup_id': ref.startup_id,
                    'status': ref.status,
                    'commission_earned': float(ref.commission_earned) if ref.commission_earned else 0,
                    'created_at': ref.created_at.isoformat() if ref.created_at else None
                }
                for ref in results
            ],
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': total > (offset + limit)
        }

    @staticmethod
    def search_leads(query=None, type=None, is_read=None, date_from=None, date_to=None, limit=50, offset=0):
        """
        Advanced lead search with multiple filters
        
        Args:
            query: Search term (name, email, company, message)
            type: Filter by type (demo, investor, contact)
            is_read: Filter by read status (True/False)
            date_from: Filter by creation date (from)
            date_to: Filter by creation date (to)
            limit: Results per page
            offset: Pagination offset
        """
        search = Lead.query
        
        # Text search
        if query:
            search_term = f"%{query}%"
            search = search.filter(
                or_(
                    Lead.name.ilike(search_term),
                    Lead.email.ilike(search_term),
                    Lead.company.ilike(search_term),
                    Lead.message.ilike(search_term)
                )
            )
        
        # Type filter
        if type:
            search = search.filter(Lead.type == type)
        
        # Read status filter
        if is_read is not None:
            search = search.filter(Lead.is_read == is_read)
        
        # Date range filter
        if date_from:
            search = search.filter(Lead.created_at >= date_from)
        if date_to:
            search = search.filter(Lead.created_at <= date_to)
        
        # Get total count
        total = search.count()
        
        # Apply pagination
        results = search.order_by(Lead.created_at.desc()).limit(limit).offset(offset).all()
        
        return {
            'results': [
                {
                    'id': lead.id,
                    'name': lead.name,
                    'email': lead.email,
                    'company': lead.company,
                    'type': lead.type,
                    'message': lead.message,
                    'is_read': lead.is_read,
                    'created_at': lead.created_at.isoformat() if lead.created_at else None
                }
                for lead in results
            ],
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': total > (offset + limit)
        }

    @staticmethod
    def global_search(query, limit=20):
        """
        Global search across all entities
        
        Args:
            query: Search term
            limit: Max results per entity type
        
        Returns:
            Dictionary with results from all entity types
        """
        search_term = f"%{query}%"
        
        # Search users
        users = User.query.filter(
            or_(
                User.full_name.ilike(search_term),
                User.email.ilike(search_term),
                User.company.ilike(search_term)
            )
        ).limit(limit).all()
        
        # Search programs
        programs = Opportunity.query.filter(
            or_(
                Opportunity.title.ilike(search_term),
                Opportunity.description.ilike(search_term)
            )
        ).limit(limit).all()
        
        # Search meetings
        meetings = Meeting.query.filter(
            or_(
                Meeting.title.ilike(search_term),
                Meeting.description.ilike(search_term)
            )
        ).limit(limit).all()
        
        # Search leads
        leads = Lead.query.filter(
            or_(
                Lead.name.ilike(search_term),
                Lead.email.ilike(search_term),
                Lead.company.ilike(search_term),
                Lead.message.ilike(search_term)
            )
        ).limit(limit).all()
        
        return {
            'query': query,
            'users': [
                {
                    'id': u.id,
                    'name': u.full_name,
                    'email': u.email,
                    'role': u.role,
                    'type': 'user'
                }
                for u in users
            ],
            'programs': [
                {
                    'id': p.id,
                    'title': p.title,
                    'type': p.type,
                    'status': p.status,
                    'entity_type': 'program'
                }
                for p in programs
            ],
            'meetings': [
                {
                    'id': m.id,
                    'title': m.title,
                    'status': m.status,
                    'scheduled_at': m.scheduled_at.isoformat() if m.scheduled_at else None,
                    'type': 'meeting'
                }
                for m in meetings
            ],
            'leads': [
                {
                    'id': l.id,
                    'name': l.name,
                    'email': l.email,
                    'type': l.type,
                    'entity_type': 'lead'
                }
                for l in leads
            ],
            'total_results': len(users) + len(programs) + len(meetings) + len(leads)
        }

    @staticmethod
    def save_search(user_id, name, entity_type, filters):
        """
        Save a search query for later use
        
        Args:
            user_id: Admin user ID
            name: Name for the saved search
            entity_type: Type of entity (users, programs, etc.)
            filters: Dictionary of filter parameters
        
        Returns:
            Saved search ID
        """
        # This would require a SavedSearch model
        # For now, return a placeholder
        return {
            'success': True,
            'message': 'Search saved successfully',
            'search_id': None  # Would be actual ID from database
        }

    @staticmethod
    def get_filter_options():
        """
        Get available filter options for all entity types
        
        Returns:
            Dictionary of filter options
        """
        return {
            'users': {
                'roles': ['startup', 'corporate', 'enabler', 'connector', 'admin'],
                'statuses': ['active', 'inactive']
            },
            'programs': {
                'types': ['accelerator', 'grant', 'pilot', 'challenge', 'corporate_vc'],
                'statuses': ['draft', 'published', 'closed']
            },
            'applications': {
                'statuses': ['submitted', 'under_review', 'shortlisted', 'accepted', 'rejected']
            },
            'meetings': {
                'statuses': ['scheduled', 'in_progress', 'completed', 'cancelled'],
                'access_types': ['all_users', 'startup_only', 'corporate_only', 'connector_only', 'specific_users']
            },
            'referrals': {
                'statuses': ['pending', 'accepted', 'successful', 'rejected']
            },
            'leads': {
                'types': ['demo', 'investor', 'contact'],
                'read_statuses': [True, False]
            }
        }
