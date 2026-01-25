# routes/webrtc.py - WebRTC Signaling Server
from flask import request
from flask_socketio import emit, join_room, leave_room, rooms
from flask_login import current_user
from extensions import socketio
from models import Meeting, MeetingParticipant, User
import json
from datetime import datetime

# Store active meeting participants
active_participants = {}

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    if current_user.is_authenticated:
        print(f'User {current_user.name} connected to WebRTC signaling server')
        emit('connected', {'status': 'Connected to signaling server'})
    else:
        print('Unauthenticated user attempted to connect')
        return False

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    if current_user.is_authenticated:
        print(f'User {current_user.name} disconnected from signaling server')
        
        # Remove user from all meeting rooms
        user_rooms = [room for room in rooms() if room.startswith('meeting_')]
        for room in user_rooms:
            leave_room(room)
            meeting_id = room.replace('meeting_', '')
            
            # Notify other participants
            emit('participant_left', {
                'user_id': current_user.id,
                'user_name': current_user.name
            }, room=room, include_self=False)
            
            # Update participant count
            if meeting_id in active_participants:
                active_participants[meeting_id].discard(current_user.id)
                if not active_participants[meeting_id]:
                    del active_participants[meeting_id]

@socketio.on('join_meeting')
def handle_join_meeting(data):
    """Handle user joining a meeting room"""
    if not current_user.is_authenticated:
        emit('error', {'message': 'Authentication required'})
        return
    
    meeting_room_id = data.get('meeting_room_id')
    if not meeting_room_id:
        emit('error', {'message': 'Meeting room ID required'})
        return
    
    # Verify user has access to this meeting
    meeting = Meeting.query.filter_by(meeting_room_id=meeting_room_id).first()
    if not meeting:
        emit('error', {'message': 'Meeting not found'})
        return
    
    # Check if user is a participant or is an admin (admins can join any meeting)
    participant = MeetingParticipant.query.filter_by(
        meeting_id=meeting.id,
        user_id=current_user.id
    ).first()
    
    # If not a participant, check if user is admin
    if not participant and current_user.role == "admin":
        # Create participant entry for admin user
        participant = MeetingParticipant(
            meeting_id=meeting.id,
            user_id=current_user.id,
            is_moderator=True  # Admins are always moderators
        )
        db.session.add(participant)
        try:
            db.session.commit()
        except Exception as e:
            print(f"Error adding admin as participant: {e}")
            db.session.rollback()
    
    if not participant:
        emit('error', {'message': 'Access denied to this meeting'})
        return
    
    # Join the meeting room
    room_name = f'meeting_{meeting_room_id}'
    join_room(room_name)
    
    # Track active participants
    if meeting_room_id not in active_participants:
        active_participants[meeting_room_id] = set()
    active_participants[meeting_room_id].add(current_user.id)
    
    # Update participant status in database
    participant.joined_at = datetime.utcnow()
    participant.attendance_status = 'joined'
    
    try:
        from extensions import db
        db.session.commit()
    except Exception as e:
        print(f"Error updating participant status: {e}")
    
    # Get current participants in the room
    current_participants = []
    if meeting_room_id in active_participants:
        for user_id in active_participants[meeting_room_id]:
            user = User.query.get(user_id)
            if user:
                current_participants.append({
                    'user_id': user.id,
                    'user_name': user.name,
                    'user_role': user.role
                })
    
    # Notify existing participants about new user
    emit('participant_joined', {
        'user_id': current_user.id,
        'user_name': current_user.name,
        'user_role': current_user.role,
        'participant_count': len(active_participants[meeting_room_id])
    }, room=room_name, include_self=False)
    
    # Send current participants list to the new user
    emit('meeting_joined', {
        'meeting_id': meeting.id,
        'meeting_title': meeting.title,
        'participants': current_participants,
        'participant_count': len(active_participants[meeting_room_id]),
        'is_moderator': participant.is_moderator
    })
    
    print(f'User {current_user.name} joined meeting {meeting.title}')

@socketio.on('leave_meeting')
def handle_leave_meeting(data):
    """Handle user leaving a meeting room"""
    if not current_user.is_authenticated:
        return
    
    meeting_room_id = data.get('meeting_room_id')
    if not meeting_room_id:
        return
    
    room_name = f'meeting_{meeting_room_id}'
    leave_room(room_name)
    
    # Update participant tracking
    if meeting_room_id in active_participants:
        active_participants[meeting_room_id].discard(current_user.id)
        if not active_participants[meeting_room_id]:
            del active_participants[meeting_room_id]
    
    # Update participant status in database
    meeting = Meeting.query.filter_by(meeting_room_id=meeting_room_id).first()
    if meeting:
        participant = MeetingParticipant.query.filter_by(
            meeting_id=meeting.id,
            user_id=current_user.id
        ).first()
        
        if participant:
            participant.left_at = datetime.utcnow()
            participant.attendance_status = 'left'
            
            try:
                from extensions import db
                db.session.commit()
            except Exception as e:
                print(f"Error updating participant status: {e}")
    
    # Notify other participants
    participant_count = len(active_participants.get(meeting_room_id, set()))
    emit('participant_left', {
        'user_id': current_user.id,
        'user_name': current_user.name,
        'participant_count': participant_count
    }, room=room_name)
    
    emit('meeting_left', {'status': 'Left meeting successfully'})
    print(f'User {current_user.name} left meeting {meeting_room_id}')

# WebRTC Signaling Events
@socketio.on('webrtc_offer')
def handle_webrtc_offer(data):
    """Handle WebRTC offer for peer connection"""
    if not current_user.is_authenticated:
        return
    
    meeting_room_id = data.get('meeting_room_id')
    target_user_id = data.get('target_user_id')
    offer = data.get('offer')
    
    if not all([meeting_room_id, target_user_id, offer]):
        emit('error', {'message': 'Missing required WebRTC offer data'})
        return
    
    room_name = f'meeting_{meeting_room_id}'
    
    # Send offer to specific user
    emit('webrtc_offer', {
        'from_user_id': current_user.id,
        'from_user_name': current_user.name,
        'offer': offer,
        'meeting_room_id': meeting_room_id
    }, room=room_name, include_self=False)

@socketio.on('webrtc_answer')
def handle_webrtc_answer(data):
    """Handle WebRTC answer for peer connection"""
    if not current_user.is_authenticated:
        return
    
    meeting_room_id = data.get('meeting_room_id')
    target_user_id = data.get('target_user_id')
    answer = data.get('answer')
    
    if not all([meeting_room_id, target_user_id, answer]):
        emit('error', {'message': 'Missing required WebRTC answer data'})
        return
    
    room_name = f'meeting_{meeting_room_id}'
    
    # Send answer to specific user
    emit('webrtc_answer', {
        'from_user_id': current_user.id,
        'from_user_name': current_user.name,
        'answer': answer,
        'meeting_room_id': meeting_room_id
    }, room=room_name, include_self=False)

@socketio.on('webrtc_ice_candidate')
def handle_ice_candidate(data):
    """Handle ICE candidate for WebRTC connection"""
    if not current_user.is_authenticated:
        return
    
    meeting_room_id = data.get('meeting_room_id')
    candidate = data.get('candidate')
    
    if not all([meeting_room_id, candidate]):
        emit('error', {'message': 'Missing required ICE candidate data'})
        return
    
    room_name = f'meeting_{meeting_room_id}'
    
    # Broadcast ICE candidate to all other participants
    emit('webrtc_ice_candidate', {
        'from_user_id': current_user.id,
        'from_user_name': current_user.name,
        'candidate': candidate,
        'meeting_room_id': meeting_room_id
    }, room=room_name, include_self=False)

# Meeting Control Events
@socketio.on('toggle_audio')
def handle_toggle_audio(data):
    """Handle audio mute/unmute"""
    if not current_user.is_authenticated:
        return
    
    meeting_room_id = data.get('meeting_room_id')
    is_muted = data.get('is_muted', False)
    
    room_name = f'meeting_{meeting_room_id}'
    
    # Notify other participants about audio status
    emit('participant_audio_changed', {
        'user_id': current_user.id,
        'user_name': current_user.name,
        'is_muted': is_muted
    }, room=room_name, include_self=False)

@socketio.on('toggle_video')
def handle_toggle_video(data):
    """Handle video on/off"""
    if not current_user.is_authenticated:
        return
    
    meeting_room_id = data.get('meeting_room_id')
    is_video_off = data.get('is_video_off', False)
    
    room_name = f'meeting_{meeting_room_id}'
    
    # Notify other participants about video status
    emit('participant_video_changed', {
        'user_id': current_user.id,
        'user_name': current_user.name,
        'is_video_off': is_video_off
    }, room=room_name, include_self=False)

@socketio.on('screen_share_start')
def handle_screen_share_start(data):
    """Handle screen sharing start"""
    if not current_user.is_authenticated:
        return
    
    meeting_room_id = data.get('meeting_room_id')
    room_name = f'meeting_{meeting_room_id}'
    
    # Notify other participants about screen sharing
    emit('participant_screen_share_started', {
        'user_id': current_user.id,
        'user_name': current_user.name
    }, room=room_name, include_self=False)

@socketio.on('screen_share_stop')
def handle_screen_share_stop(data):
    """Handle screen sharing stop"""
    if not current_user.is_authenticated:
        return
    
    meeting_room_id = data.get('meeting_room_id')
    room_name = f'meeting_{meeting_room_id}'
    
    # Notify other participants about screen sharing stop
    emit('participant_screen_share_stopped', {
        'user_id': current_user.id,
        'user_name': current_user.name
    }, room=room_name, include_self=False)

@socketio.on('chat_message')
def handle_chat_message(data):
    """Handle chat messages in meeting"""
    if not current_user.is_authenticated:
        return
    
    meeting_room_id = data.get('meeting_room_id')
    message = data.get('message', '').strip()
    
    if not message:
        return
    
    room_name = f'meeting_{meeting_room_id}'
    
    # Broadcast chat message to all participants
    emit('chat_message', {
        'user_id': current_user.id,
        'user_name': current_user.name,
        'user_role': current_user.role,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room_name)

# Meeting Statistics
@socketio.on('get_meeting_stats')
def handle_get_meeting_stats(data):
    """Get real-time meeting statistics"""
    if not current_user.is_authenticated:
        return
    
    meeting_room_id = data.get('meeting_room_id')
    
    if meeting_room_id in active_participants:
        participant_count = len(active_participants[meeting_room_id])
        
        # Get participant details
        participants = []
        for user_id in active_participants[meeting_room_id]:
            user = User.query.get(user_id)
            if user:
                participants.append({
                    'user_id': user.id,
                    'user_name': user.name,
                    'user_role': user.role
                })
        
        emit('meeting_stats', {
            'participant_count': participant_count,
            'participants': participants,
            'meeting_room_id': meeting_room_id
        })
    else:
@socketio.on('admin_mute_user')
def handle_admin_mute_user(data):
    """Handle admin muting a user"""
    if not current_user.is_authenticated or current_user.role != 'admin':
        return
    
    meeting_room_id = data.get('meeting_room_id')
    target_user_id = data.get('target_user_id')
    
    if not meeting_room_id or not target_user_id:
        return
        
    room_name = f'meeting_{meeting_room_id}'
    
    # Broadcast mute command to the target user/all users
    emit('force_mute', {
        'target_user_id': target_user_id,
        'by_admin': True
    }, room=room_name)
    
    # Also update UI state for everyone
    emit('participant_audio_changed', {
        'user_id': target_user_id,
        'is_muted': True
    }, room=room_name)


@socketio.on('admin_kick_user')
def handle_admin_kick_user(data):
    """Handle admin kicking a user"""
    if not current_user.is_authenticated or current_user.role != 'admin':
        return
    
    meeting_room_id = data.get('meeting_room_id')
    target_user_id = data.get('target_user_id')
    
    if not meeting_room_id or not target_user_id:
        return
        
    room_name = f'meeting_{meeting_room_id}'
    
    # Broadcast kick command to all
    emit('force_kick', {
        'target_user_id': target_user_id,
        'by_admin': True
    }, room=room_name)
    
    # Actually remove them from backend tracking if needed
    if meeting_room_id in active_participants:
        active_participants[meeting_room_id].discard(target_user_id)