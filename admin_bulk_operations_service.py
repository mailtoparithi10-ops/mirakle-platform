"""
Admin Bulk Operations Service
Provides bulk action capabilities for efficient admin management
"""

from models import db, User, Opportunity, Application, Meeting, Referral, Lead
from datetime import datetime
from sqlalchemy import and_, or_
import csv
from io import StringIO


class AdminBulkOperationsService:
    """Service for performing bulk operations on entities"""

    @staticmethod
    def bulk_update_users(user_ids, updates):
        """
        Bulk update multiple users
        
        Args:
            user_ids: List of user IDs to update
            updates: Dictionary of fields to update
        
        Returns:
            Dictionary with success status and count
        """
        try:
            # Validate updates
            allowed_fields = ['role', 'status', 'country', 'company']
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
            
            if not filtered_updates:
                return {
                    'success': False,
                    'error': 'No valid fields to update',
                    'updated_count': 0
                }
            
            # Perform bulk update
            result = User.query.filter(User.id.in_(user_ids)).update(
                filtered_updates,
                synchronize_session=False
            )
            
            db.session.commit()
            
            return {
                'success': True,
                'updated_count': result,
                'message': f'Successfully updated {result} users'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'updated_count': 0
            }

    @staticmethod
    def bulk_delete_users(user_ids, confirm=False):
        """
        Bulk delete multiple users
        
        Args:
            user_ids: List of user IDs to delete
            confirm: Confirmation flag (must be True)
        
        Returns:
            Dictionary with success status and count
        """
        if not confirm:
            return {
                'success': False,
                'error': 'Confirmation required for bulk delete',
                'deleted_count': 0
            }
        
        try:
            # Don't allow deleting admin users
            admin_count = User.query.filter(
                and_(User.id.in_(user_ids), User.role == 'admin')
            ).count()
            
            if admin_count > 0:
                return {
                    'success': False,
                    'error': 'Cannot delete admin users',
                    'deleted_count': 0
                }
            
            # Perform bulk delete
            result = User.query.filter(User.id.in_(user_ids)).delete(
                synchronize_session=False
            )
            
            db.session.commit()
            
            return {
                'success': True,
                'deleted_count': result,
                'message': f'Successfully deleted {result} users'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'deleted_count': 0
            }

    @staticmethod
    def bulk_export_users(user_ids=None, format='csv'):
        """
        Bulk export users to CSV
        
        Args:
            user_ids: List of user IDs to export (None = all)
            format: Export format (csv, json)
        
        Returns:
            CSV or JSON string
        """
        query = User.query
        
        if user_ids:
            query = query.filter(User.id.in_(user_ids))
        
        users = query.all()
        
        if format == 'csv':
            output = StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow([
                'ID', 'Full Name', 'Email', 'Role', 'Company', 
                'Country', 'Created At', 'Status'
            ])
            
            # Data
            for user in users:
                writer.writerow([
                    user.id,
                    user.full_name,
                    user.email,
                    user.role,
                    user.company if hasattr(user, 'company') else '',
                    user.country if hasattr(user, 'country') else '',
                    user.created_at.isoformat() if user.created_at else '',
                    getattr(user, 'status', 'active')
                ])
            
            return output.getvalue()
        
        elif format == 'json':
            return {
                'users': [
                    {
                        'id': user.id,
                        'full_name': user.full_name,
                        'email': user.email,
                        'role': user.role,
                        'company': user.company if hasattr(user, 'company') else None,
                        'country': user.country if hasattr(user, 'country') else None,
                        'created_at': user.created_at.isoformat() if user.created_at else None
                    }
                    for user in users
                ],
                'total': len(users)
            }

    @staticmethod
    def bulk_update_programs(program_ids, updates):
        """
        Bulk update multiple programs
        
        Args:
            program_ids: List of program IDs to update
            updates: Dictionary of fields to update
        
        Returns:
            Dictionary with success status and count
        """
        try:
            allowed_fields = ['status', 'type', 'deadline']
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
            
            if not filtered_updates:
                return {
                    'success': False,
                    'error': 'No valid fields to update',
                    'updated_count': 0
                }
            
            # Convert deadline string to datetime if present
            if 'deadline' in filtered_updates and isinstance(filtered_updates['deadline'], str):
                filtered_updates['deadline'] = datetime.fromisoformat(filtered_updates['deadline'])
            
            result = Opportunity.query.filter(Opportunity.id.in_(program_ids)).update(
                filtered_updates,
                synchronize_session=False
            )
            
            db.session.commit()
            
            return {
                'success': True,
                'updated_count': result,
                'message': f'Successfully updated {result} programs'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'updated_count': 0
            }

    @staticmethod
    def bulk_delete_programs(program_ids, confirm=False):
        """
        Bulk delete multiple programs
        
        Args:
            program_ids: List of program IDs to delete
            confirm: Confirmation flag (must be True)
        
        Returns:
            Dictionary with success status and count
        """
        if not confirm:
            return {
                'success': False,
                'error': 'Confirmation required for bulk delete',
                'deleted_count': 0
            }
        
        try:
            # Check for associated applications
            app_count = Application.query.filter(
                Application.opportunity_id.in_(program_ids)
            ).count()
            
            if app_count > 0:
                return {
                    'success': False,
                    'error': f'Cannot delete programs with {app_count} associated applications',
                    'deleted_count': 0
                }
            
            result = Opportunity.query.filter(Opportunity.id.in_(program_ids)).delete(
                synchronize_session=False
            )
            
            db.session.commit()
            
            return {
                'success': True,
                'deleted_count': result,
                'message': f'Successfully deleted {result} programs'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'deleted_count': 0
            }

    @staticmethod
    def bulk_update_application_status(application_ids, status, note=None):
        """
        Bulk update application statuses
        
        Args:
            application_ids: List of application IDs
            status: New status
            note: Optional note for the status change
        
        Returns:
            Dictionary with success status and count
        """
        try:
            valid_statuses = ['submitted', 'under_review', 'shortlisted', 'accepted', 'rejected']
            
            if status not in valid_statuses:
                return {
                    'success': False,
                    'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}',
                    'updated_count': 0
                }
            
            updates = {'status': status}
            if note:
                updates['admin_note'] = note
            
            result = Application.query.filter(Application.id.in_(application_ids)).update(
                updates,
                synchronize_session=False
            )
            
            db.session.commit()
            
            return {
                'success': True,
                'updated_count': result,
                'message': f'Successfully updated {result} applications to {status}'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'updated_count': 0
            }

    @staticmethod
    def bulk_delete_meetings(meeting_ids, confirm=False):
        """
        Bulk delete multiple meetings
        
        Args:
            meeting_ids: List of meeting IDs to delete
            confirm: Confirmation flag (must be True)
        
        Returns:
            Dictionary with success status and count
        """
        if not confirm:
            return {
                'success': False,
                'error': 'Confirmation required for bulk delete',
                'deleted_count': 0
            }
        
        try:
            # Don't delete in-progress meetings
            in_progress = Meeting.query.filter(
                and_(Meeting.id.in_(meeting_ids), Meeting.status == 'in_progress')
            ).count()
            
            if in_progress > 0:
                return {
                    'success': False,
                    'error': f'Cannot delete {in_progress} in-progress meetings',
                    'deleted_count': 0
                }
            
            result = Meeting.query.filter(Meeting.id.in_(meeting_ids)).delete(
                synchronize_session=False
            )
            
            db.session.commit()
            
            return {
                'success': True,
                'deleted_count': result,
                'message': f'Successfully deleted {result} meetings'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'deleted_count': 0
            }

    @staticmethod
    def bulk_update_meeting_status(meeting_ids, status):
        """
        Bulk update meeting statuses
        
        Args:
            meeting_ids: List of meeting IDs
            status: New status
        
        Returns:
            Dictionary with success status and count
        """
        try:
            valid_statuses = ['scheduled', 'in_progress', 'completed', 'cancelled']
            
            if status not in valid_statuses:
                return {
                    'success': False,
                    'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}',
                    'updated_count': 0
                }
            
            result = Meeting.query.filter(Meeting.id.in_(meeting_ids)).update(
                {'status': status},
                synchronize_session=False
            )
            
            db.session.commit()
            
            return {
                'success': True,
                'updated_count': result,
                'message': f'Successfully updated {result} meetings to {status}'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'updated_count': 0
            }

    @staticmethod
    def bulk_mark_leads_read(lead_ids):
        """
        Bulk mark leads as read
        
        Args:
            lead_ids: List of lead IDs
        
        Returns:
            Dictionary with success status and count
        """
        try:
            result = Lead.query.filter(Lead.id.in_(lead_ids)).update(
                {'is_read': True},
                synchronize_session=False
            )
            
            db.session.commit()
            
            return {
                'success': True,
                'updated_count': result,
                'message': f'Successfully marked {result} leads as read'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'updated_count': 0
            }

    @staticmethod
    def bulk_delete_leads(lead_ids, confirm=False):
        """
        Bulk delete multiple leads
        
        Args:
            lead_ids: List of lead IDs to delete
            confirm: Confirmation flag (must be True)
        
        Returns:
            Dictionary with success status and count
        """
        if not confirm:
            return {
                'success': False,
                'error': 'Confirmation required for bulk delete',
                'deleted_count': 0
            }
        
        try:
            result = Lead.query.filter(Lead.id.in_(lead_ids)).delete(
                synchronize_session=False
            )
            
            db.session.commit()
            
            return {
                'success': True,
                'deleted_count': result,
                'message': f'Successfully deleted {result} leads'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'deleted_count': 0
            }

    @staticmethod
    def bulk_update_referral_status(referral_ids, status):
        """
        Bulk update referral statuses
        
        Args:
            referral_ids: List of referral IDs
            status: New status
        
        Returns:
            Dictionary with success status and count
        """
        try:
            valid_statuses = ['pending', 'accepted', 'successful', 'rejected']
            
            if status not in valid_statuses:
                return {
                    'success': False,
                    'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}',
                    'updated_count': 0
                }
            
            result = Referral.query.filter(Referral.id.in_(referral_ids)).update(
                {'status': status},
                synchronize_session=False
            )
            
            db.session.commit()
            
            return {
                'success': True,
                'updated_count': result,
                'message': f'Successfully updated {result} referrals to {status}'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'updated_count': 0
            }

    @staticmethod
    def get_bulk_operation_summary(entity_type, entity_ids):
        """
        Get summary of entities before bulk operation
        
        Args:
            entity_type: Type of entity (users, programs, etc.)
            entity_ids: List of entity IDs
        
        Returns:
            Summary dictionary
        """
        if entity_type == 'users':
            users = User.query.filter(User.id.in_(entity_ids)).all()
            return {
                'total': len(users),
                'by_role': {
                    role: len([u for u in users if u.role == role])
                    for role in set(u.role for u in users)
                },
                'admin_count': len([u for u in users if u.role == 'admin'])
            }
        
        elif entity_type == 'programs':
            programs = Opportunity.query.filter(Opportunity.id.in_(entity_ids)).all()
            app_count = Application.query.filter(
                Application.opportunity_id.in_(entity_ids)
            ).count()
            
            return {
                'total': len(programs),
                'by_status': {
                    status: len([p for p in programs if p.status == status])
                    for status in set(p.status for p in programs)
                },
                'associated_applications': app_count
            }
        
        elif entity_type == 'applications':
            applications = Application.query.filter(Application.id.in_(entity_ids)).all()
            return {
                'total': len(applications),
                'by_status': {
                    status: len([a for a in applications if a.status == status])
                    for status in set(a.status for a in applications)
                }
            }
        
        elif entity_type == 'meetings':
            meetings = Meeting.query.filter(Meeting.id.in_(entity_ids)).all()
            return {
                'total': len(meetings),
                'by_status': {
                    status: len([m for m in meetings if m.status == status])
                    for status in set(m.status for m in meetings)
                },
                'in_progress_count': len([m for m in meetings if m.status == 'in_progress'])
            }
        
        elif entity_type == 'leads':
            leads = Lead.query.filter(Lead.id.in_(entity_ids)).all()
            return {
                'total': len(leads),
                'by_type': {
                    type: len([l for l in leads if l.type == type])
                    for type in set(l.type for l in leads)
                },
                'unread_count': len([l for l in leads if not l.is_read])
            }
        
        elif entity_type == 'referrals':
            referrals = Referral.query.filter(Referral.id.in_(entity_ids)).all()
            return {
                'total': len(referrals),
                'by_status': {
                    status: len([r for r in referrals if r.status == status])
                    for status in set(r.status for r in referrals)
                }
            }
        
        return {'total': 0}
