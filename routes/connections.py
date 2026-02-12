# routes/connections.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Connection, User, Notification, Startup
from datetime import datetime
from analytics_service import AnalyticsService
from sqlalchemy import or_, and_

bp = Blueprint('connections', __name__, url_prefix='/api/connections')


@bp.route('/', methods=['GET'])
@login_required
def get_connections():
    """Get all connections for current user"""
    # Get accepted connections where user is either requester or recipient
    connections = Connection.query.filter(
        Connection.status == 'accepted',
        or_(
            Connection.requester_id == current_user.id,
            Connection.recipient_id == current_user.id
        )
    ).order_by(Connection.accepted_at.desc()).all()
    
    # Format connections with other user's info
    formatted_connections = []
    for conn in connections:
        other_user_id = conn.recipient_id if conn.requester_id == current_user.id else conn.requester_id
        other_user = User.query.get(other_user_id)
        
        if other_user:
            formatted_connections.append({
                'connection_id': conn.id,
                'user': {
                    'id': other_user.id,
                    'name': other_user.name,
                    'email': other_user.email,
                    'profile_pic': other_user.profile_pic,
                    'role': other_user.role,
                    'company': other_user.company,
                    'region': other_user.region
                },
                'connected_at': conn.accepted_at.isoformat() if conn.accepted_at else None
            })
    
    return jsonify({
        'success': True,
        'connections': formatted_connections,
        'count': len(formatted_connections)
    })


@bp.route('/requests', methods=['GET'])
@login_required
def get_connection_requests():
    """Get pending connection requests (received and sent)"""
    # Received requests
    received = Connection.query.filter(
        Connection.recipient_id == current_user.id,
        Connection.status == 'pending'
    ).order_by(Connection.created_at.desc()).all()
    
    # Sent requests
    sent = Connection.query.filter(
        Connection.requester_id == current_user.id,
        Connection.status == 'pending'
    ).order_by(Connection.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'received': [req.to_dict() for req in received],
        'sent': [req.to_dict() for req in sent]
    })


@bp.route('/suggestions', methods=['GET'])
@login_required
def get_suggestions():
    """Get suggested connections based on user profile and activity"""
    limit = request.args.get('limit', 10, type=int)
    
    # Get users already connected or with pending requests
    existing_connections = db.session.query(Connection.requester_id, Connection.recipient_id).filter(
        or_(
            Connection.requester_id == current_user.id,
            Connection.recipient_id == current_user.id
        )
    ).all()
    
    excluded_ids = {current_user.id}
    for req_id, rec_id in existing_connections:
        excluded_ids.add(req_id)
        excluded_ids.add(rec_id)
    
    # Suggestion algorithm
    suggestions = []
    
    # 1. Same role users (enablers, corporates, investors)
    if current_user.role == 'founder':
        # Suggest enablers and corporates
        role_matches = User.query.filter(
            User.role.in_(['enabler', 'corporate']),
            User.id.notin_(excluded_ids),
            User.is_active == True
        ).limit(limit // 2).all()
        suggestions.extend(role_matches)
    
    # 2. Same region/country users
    if current_user.region:
        region_matches = User.query.filter(
            User.region == current_user.region,
            User.id.notin_(excluded_ids),
            User.is_active == True,
            User.id.notin_([u.id for u in suggestions])
        ).limit(limit // 3).all()
        suggestions.extend(region_matches)
    
    # 3. Users with similar sectors (for founders)
    if current_user.role == 'founder':
        startup = Startup.query.filter_by(founder_id=current_user.id).first()
        if startup and startup.sectors:
            import json
            user_sectors = json.loads(startup.sectors or '[]')
            
            # Find other startups with overlapping sectors
            similar_startups = Startup.query.filter(
                Startup.founder_id.notin_(excluded_ids),
                Startup.founder_id != current_user.id
            ).all()
            
            for s in similar_startups:
                s_sectors = json.loads(s.sectors or '[]')
                if any(sector in s_sectors for sector in user_sectors):
                    founder = User.query.get(s.founder_id)
                    if founder and founder not in suggestions:
                        suggestions.append(founder)
                        if len(suggestions) >= limit:
                            break
    
    # 4. Fill remaining with random active users
    if len(suggestions) < limit:
        remaining = limit - len(suggestions)
        random_users = User.query.filter(
            User.id.notin_(excluded_ids),
            User.id.notin_([u.id for u in suggestions]),
            User.is_active == True
        ).limit(remaining).all()
        suggestions.extend(random_users)
    
    # Format suggestions
    formatted_suggestions = []
    for user in suggestions[:limit]:
        formatted_suggestions.append({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'profile_pic': user.profile_pic,
            'role': user.role,
            'company': user.company,
            'region': user.region,
            'country': user.country
        })
    
    return jsonify({
        'success': True,
        'suggestions': formatted_suggestions
    })


@bp.route('/request', methods=['POST'])
@login_required
def send_connection_request():
    """Send a connection request to another user"""
    data = request.get_json()
    recipient_id = data.get('recipient_id')
    message = data.get('message', '')
    
    if not recipient_id:
        return jsonify({'success': False, 'message': 'Recipient ID required'}), 400
    
    if recipient_id == current_user.id:
        return jsonify({'success': False, 'message': 'Cannot connect with yourself'}), 400
    
    # Check if recipient exists
    recipient = User.query.get(recipient_id)
    if not recipient:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    # Check if connection already exists
    existing = Connection.query.filter(
        or_(
            and_(Connection.requester_id == current_user.id, Connection.recipient_id == recipient_id),
            and_(Connection.requester_id == recipient_id, Connection.recipient_id == current_user.id)
        )
    ).first()
    
    if existing:
        if existing.status == 'accepted':
            return jsonify({'success': False, 'message': 'Already connected'}), 400
        elif existing.status == 'pending':
            return jsonify({'success': False, 'message': 'Connection request already sent'}), 400
        elif existing.status == 'rejected':
            # Allow re-requesting after rejection
            existing.status = 'pending'
            existing.created_at = datetime.utcnow()
            existing.message = message
            db.session.commit()
            return jsonify({'success': True, 'connection': existing.to_dict()})
    
    # Create new connection request
    connection = Connection(
        requester_id=current_user.id,
        recipient_id=recipient_id,
        message=message,
        status='pending'
    )
    db.session.add(connection)
    
    # Create notification
    notification = Notification(
        user_id=recipient_id,
        title='New Connection Request',
        message=f'{current_user.name} wants to connect with you',
        type='info',
        link='/connections'
    )
    db.session.add(notification)
    
    # Track analytics
    AnalyticsService.track_event(
        event_type='connection_requested',
        user_id=current_user.id,
        event_data={'recipient_id': recipient_id}
    )
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'connection': connection.to_dict()
    })


@bp.route('/<int:connection_id>/accept', methods=['PUT'])
@login_required
def accept_connection(connection_id):
    """Accept a connection request"""
    connection = Connection.query.get(connection_id)
    
    if not connection:
        return jsonify({'success': False, 'message': 'Connection not found'}), 404
    
    if connection.recipient_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    if connection.status != 'pending':
        return jsonify({'success': False, 'message': 'Connection request not pending'}), 400
    
    connection.status = 'accepted'
    connection.accepted_at = datetime.utcnow()
    
    # Create notification for requester
    notification = Notification(
        user_id=connection.requester_id,
        title='Connection Accepted',
        message=f'{current_user.name} accepted your connection request',
        type='success',
        link='/connections'
    )
    db.session.add(notification)
    
    # Track analytics for both users
    AnalyticsService.track_event(
        event_type='connection_made',
        user_id=current_user.id,
        event_data={'connected_with': connection.requester_id}
    )
    AnalyticsService.track_event(
        event_type='connection_made',
        user_id=connection.requester_id,
        event_data={'connected_with': current_user.id}
    )
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'connection': connection.to_dict()
    })


@bp.route('/<int:connection_id>/reject', methods=['PUT'])
@login_required
def reject_connection(connection_id):
    """Reject a connection request"""
    connection = Connection.query.get(connection_id)
    
    if not connection:
        return jsonify({'success': False, 'message': 'Connection not found'}), 404
    
    if connection.recipient_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    if connection.status != 'pending':
        return jsonify({'success': False, 'message': 'Connection request not pending'}), 400
    
    connection.status = 'rejected'
    db.session.commit()
    
    return jsonify({'success': True})


@bp.route('/<int:connection_id>', methods=['DELETE'])
@login_required
def remove_connection(connection_id):
    """Remove an existing connection"""
    connection = Connection.query.get(connection_id)
    
    if not connection:
        return jsonify({'success': False, 'message': 'Connection not found'}), 404
    
    # Verify user is part of this connection
    if connection.requester_id != current_user.id and connection.recipient_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    # Get other user ID for notification
    other_user_id = connection.recipient_id if connection.requester_id == current_user.id else connection.requester_id
    
    # Delete connection
    db.session.delete(connection)
    
    # Create notification for other user
    notification = Notification(
        user_id=other_user_id,
        title='Connection Removed',
        message=f'{current_user.name} removed the connection',
        type='info',
        link='/connections'
    )
    db.session.add(notification)
    
    db.session.commit()
    
    return jsonify({'success': True})


@bp.route('/stats', methods=['GET'])
@login_required
def get_connection_stats():
    """Get connection statistics for current user"""
    # Total connections
    total = Connection.query.filter(
        Connection.status == 'accepted',
        or_(
            Connection.requester_id == current_user.id,
            Connection.recipient_id == current_user.id
        )
    ).count()
    
    # Pending requests (received)
    pending_received = Connection.query.filter(
        Connection.recipient_id == current_user.id,
        Connection.status == 'pending'
    ).count()
    
    # Pending requests (sent)
    pending_sent = Connection.query.filter(
        Connection.requester_id == current_user.id,
        Connection.status == 'pending'
    ).count()
    
    # Connections by role
    connections = Connection.query.filter(
        Connection.status == 'accepted',
        or_(
            Connection.requester_id == current_user.id,
            Connection.recipient_id == current_user.id
        )
    ).all()
    
    role_breakdown = {}
    for conn in connections:
        other_user_id = conn.recipient_id if conn.requester_id == current_user.id else conn.requester_id
        other_user = User.query.get(other_user_id)
        if other_user:
            role = other_user.role
            role_breakdown[role] = role_breakdown.get(role, 0) + 1
    
    return jsonify({
        'success': True,
        'stats': {
            'total_connections': total,
            'pending_received': pending_received,
            'pending_sent': pending_sent,
            'by_role': role_breakdown
        }
    })
