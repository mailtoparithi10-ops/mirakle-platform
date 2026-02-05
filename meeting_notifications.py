#!/usr/bin/env python3
"""
Meeting Notification Service
Handles creating and managing notifications for meeting events
"""

from models import Notification, Meeting, MeetingParticipant, User
from extensions import db
from datetime import datetime, timedelta


def create_meeting_notification(meeting_id, notification_type, custom_message=None):
    """
    Create notifications for meeting participants
    
    Args:
        meeting_id: ID of the meeting
        notification_type: Type of notification ('created', 'updated', 'reminder', 'cancelled')
        custom_message: Optional custom message
    """
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return False
    
    # Get all participants
    participants = MeetingParticipant.query.filter_by(meeting_id=meeting_id).all()
    
    # Define notification templates
    templates = {
        'created': {
            'title': f'New Meeting: {meeting.title}',
            'message': f'You have been invited to "{meeting.title}" scheduled for {meeting.scheduled_at.strftime("%B %d, %Y at %I:%M %p")}.',
            'type': 'info'
        },
        'updated': {
            'title': f'Meeting Updated: {meeting.title}',
            'message': f'The meeting "{meeting.title}" has been updated. Please check the details.',
            'type': 'warning'
        },
        'reminder': {
            'title': f'Meeting Reminder: {meeting.title}',
            'message': f'Your meeting "{meeting.title}" starts in 15 minutes. Click to join.',
            'type': 'info'
        },
        'cancelled': {
            'title': f'Meeting Cancelled: {meeting.title}',
            'message': f'The meeting "{meeting.title}" scheduled for {meeting.scheduled_at.strftime("%B %d, %Y at %I:%M %p")} has been cancelled.',
            'type': 'danger'
        },
        'starting_soon': {
            'title': f'Meeting Starting Soon: {meeting.title}',
            'message': f'Your meeting "{meeting.title}" starts in 5 minutes. Get ready to join!',
            'type': 'success'
        }
    }
    
    template = templates.get(notification_type, templates['created'])
    
    # Use custom message if provided
    if custom_message:
        template['message'] = custom_message
    
    # Create notifications for all participants
    notifications_created = 0
    for participant in participants:
        if participant.user_id:  # Only for registered users
            notification = Notification(
                user_id=participant.user_id,
                title=template['title'],
                message=template['message'],
                type=template['type'],
                link=f'/meeting/join/{meeting.meeting_room_id}'
            )
            db.session.add(notification)
            notifications_created += 1
    
    try:
        db.session.commit()
        print(f"Created {notifications_created} notifications for meeting {meeting.title}")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error creating notifications: {e}")
        return False


def send_meeting_reminders():
    """
    Send reminders for upcoming meetings (to be called by a scheduler)
    """
    now = datetime.utcnow()
    
    # Find meetings starting in 15 minutes
    reminder_time = now + timedelta(minutes=15)
    upcoming_meetings = Meeting.query.filter(
        Meeting.scheduled_at.between(now, reminder_time),
        Meeting.status == 'scheduled'
    ).all()
    
    for meeting in upcoming_meetings:
        # Check if reminder already sent (to avoid duplicates)
        existing_reminders = Notification.query.filter(
            Notification.title.like(f'Meeting Reminder: {meeting.title}%'),
            Notification.created_at > now - timedelta(hours=1)
        ).count()
        
        if existing_reminders == 0:
            create_meeting_notification(meeting.id, 'reminder')
    
    # Find meetings starting in 5 minutes
    starting_soon_time = now + timedelta(minutes=5)
    starting_soon_meetings = Meeting.query.filter(
        Meeting.scheduled_at.between(now, starting_soon_time),
        Meeting.status == 'scheduled'
    ).all()
    
    for meeting in starting_soon_meetings:
        # Check if starting soon notification already sent
        existing_notifications = Notification.query.filter(
            Notification.title.like(f'Meeting Starting Soon: {meeting.title}%'),
            Notification.created_at > now - timedelta(minutes=30)
        ).count()
        
        if existing_notifications == 0:
            create_meeting_notification(meeting.id, 'starting_soon')


def get_user_meeting_notifications(user_id, limit=10):
    """
    Get meeting-related notifications for a user
    """
    notifications = Notification.query.filter(
        Notification.user_id == user_id,
        Notification.title.like('%Meeting%')
    ).order_by(Notification.created_at.desc()).limit(limit).all()
    
    return [n.to_dict() for n in notifications]


def mark_meeting_notifications_read(user_id, meeting_id):
    """
    Mark all notifications for a specific meeting as read
    """
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return False
    
    notifications = Notification.query.filter(
        Notification.user_id == user_id,
        Notification.title.like(f'%{meeting.title}%')
    ).all()
    
    for notification in notifications:
        notification.is_read = True
    
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error marking notifications as read: {e}")
        return False


if __name__ == '__main__':
    # Test the notification system
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from app import app
    
    with app.app_context():
        print("Testing meeting notification system...")
        
        # Get a test meeting
        meeting = Meeting.query.first()
        if meeting:
            print(f"Testing with meeting: {meeting.title}")
            create_meeting_notification(meeting.id, 'reminder')
            print("Test notification created!")
        else:
            print("No meetings found for testing")