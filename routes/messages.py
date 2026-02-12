# routes/messages.py
from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from extensions import db
from models import Message, User, Notification
from datetime import datetime
from analytics_service import AnalyticsService
import uuid

bp = Blueprint('messages', __name__, url_prefix='/api/messages')
web_bp = Blueprint('messages_web', __name__, url_prefix='/messages')


# ==================== WEB ROUTES ====================

@web_bp.route('/')
@login_required
def inbox():
    """Display messages inbox page"""
    return render_template('messages_inbox.html')


# ==================== API ROUTES ====================

@bp.route('/', methods=['GET'])
@login_required
def get_messages():
    """Get all messages for current user (inbox + sent)"""
    # Get inbox messages (received, not deleted)
    inbox_messages = Message.query.filter(
        Message.recipient_id == current_user.id,
        Message.is_deleted_by_recipient == False
    ).order_by(Message.created_at.desc()).all()
    
    # Get sent messages (not deleted)
    sent_messages = Message.query.filter(
        Message.sender_id == current_user.id,
        Message.is_deleted_by_sender == False
    ).order_by(Message.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'inbox': [msg.to_dict() for msg in inbox_messages],
        'sent': [msg.to_dict() for msg in sent_messages]
    })


@bp.route('/threads', methods=['GET'])
@login_required
def get_threads():
    """Get all conversation threads for current user"""
    # Get all unique thread IDs
    threads_query = db.session.query(Message.thread_id).filter(
        db.or_(
            db.and_(Message.sender_id == current_user.id, Message.is_deleted_by_sender == False),
            db.and_(Message.recipient_id == current_user.id, Message.is_deleted_by_recipient == False)
        )
    ).distinct()
    
    threads = []
    for (thread_id,) in threads_query:
        # Get latest message in thread
        latest_msg = Message.query.filter(
            Message.thread_id == thread_id
        ).order_by(Message.created_at.desc()).first()
        
        if latest_msg:
            # Get other participant
            other_user_id = latest_msg.recipient_id if latest_msg.sender_id == current_user.id else latest_msg.sender_id
            other_user = User.query.get(other_user_id)
            
            # Count unread messages in thread
            unread_count = Message.query.filter(
                Message.thread_id == thread_id,
                Message.recipient_id == current_user.id,
                Message.is_read == False
            ).count()
            
            threads.append({
                'thread_id': thread_id,
                'other_user': {
                    'id': other_user.id,
                    'name': other_user.name,
                    'profile_pic': other_user.profile_pic,
                    'role': other_user.role,
                    'company': other_user.company
                },
                'latest_message': latest_msg.to_dict(),
                'unread_count': unread_count
            })
    
    # Sort by latest message time
    threads.sort(key=lambda x: x['latest_message']['created_at'], reverse=True)
    
    return jsonify({
        'success': True,
        'threads': threads
    })


@bp.route('/thread/<thread_id>', methods=['GET'])
@login_required
def get_thread(thread_id):
    """Get all messages in a conversation thread"""
    messages = Message.query.filter(
        Message.thread_id == thread_id,
        db.or_(
            db.and_(Message.sender_id == current_user.id, Message.is_deleted_by_sender == False),
            db.and_(Message.recipient_id == current_user.id, Message.is_deleted_by_recipient == False)
        )
    ).order_by(Message.created_at.asc()).all()
    
    # Mark received messages as read
    for msg in messages:
        if msg.recipient_id == current_user.id and not msg.is_read:
            msg.is_read = True
            msg.read_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'messages': [msg.to_dict() for msg in messages]
    })


@bp.route('/send', methods=['POST'])
@login_required
def send_message():
    """Send a new message"""
    data = request.get_json()
    
    recipient_id = data.get('recipient_id')
    subject = data.get('subject', '')
    body = data.get('body')
    thread_id = data.get('thread_id')  # Optional, for replies
    parent_message_id = data.get('parent_message_id')  # Optional
    
    if not recipient_id or not body:
        return jsonify({'success': False, 'message': 'Recipient and message body are required'}), 400
    
    # Verify recipient exists
    recipient = User.query.get(recipient_id)
    if not recipient:
        return jsonify({'success': False, 'message': 'Recipient not found'}), 404
    
    # Generate thread_id if not provided (new conversation)
    if not thread_id:
        thread_id = str(uuid.uuid4())
    
    # Create message
    message = Message(
        sender_id=current_user.id,
        recipient_id=recipient_id,
        subject=subject,
        body=body,
        thread_id=thread_id,
        parent_message_id=parent_message_id
    )
    
    db.session.add(message)
    
    # Create notification for recipient
    notification = Notification(
        user_id=recipient_id,
        title='New Message',
        message=f'{current_user.name} sent you a message',
        type='info',
        link=f'/messages?thread={thread_id}'
    )
    db.session.add(notification)
    
    # Track analytics event
    AnalyticsService.track_event(
        event_type='message_sent',
        user_id=current_user.id,
        event_data={'recipient_id': recipient_id, 'thread_id': thread_id}
    )
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': message.to_dict()
    })


@bp.route('/<int:message_id>/read', methods=['PUT'])
@login_required
def mark_as_read(message_id):
    """Mark a message as read"""
    message = Message.query.get(message_id)
    
    if not message:
        return jsonify({'success': False, 'message': 'Message not found'}), 404
    
    if message.recipient_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    message.is_read = True
    message.read_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True})


@bp.route('/<int:message_id>', methods=['DELETE'])
@login_required
def delete_message(message_id):
    """Delete a message (soft delete)"""
    message = Message.query.get(message_id)
    
    if not message:
        return jsonify({'success': False, 'message': 'Message not found'}), 404
    
    # Soft delete based on user role
    if message.sender_id == current_user.id:
        message.is_deleted_by_sender = True
    elif message.recipient_id == current_user.id:
        message.is_deleted_by_recipient = True
    else:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    # If both deleted, hard delete
    if message.is_deleted_by_sender and message.is_deleted_by_recipient:
        db.session.delete(message)
    
    db.session.commit()
    
    return jsonify({'success': True})


@bp.route('/unread-count', methods=['GET'])
@login_required
def get_unread_count():
    """Get count of unread messages"""
    count = Message.query.filter(
        Message.recipient_id == current_user.id,
        Message.is_read == False,
        Message.is_deleted_by_recipient == False
    ).count()
    
    return jsonify({
        'success': True,
        'unread_count': count
    })


@bp.route('/search', methods=['GET'])
@login_required
def search_messages():
    """Search messages by keyword"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'success': False, 'message': 'Search query required'}), 400
    
    messages = Message.query.filter(
        db.or_(
            db.and_(Message.sender_id == current_user.id, Message.is_deleted_by_sender == False),
            db.and_(Message.recipient_id == current_user.id, Message.is_deleted_by_recipient == False)
        ),
        db.or_(
            Message.subject.ilike(f'%{query}%'),
            Message.body.ilike(f'%{query}%')
        )
    ).order_by(Message.created_at.desc()).limit(50).all()
    
    return jsonify({
        'success': True,
        'messages': [msg.to_dict() for msg in messages]
    })
