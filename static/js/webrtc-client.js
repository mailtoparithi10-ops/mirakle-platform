// WebRTC Client for Real Video Calling
class WebRTCClient {
    constructor(meetingRoomId) {
        this.meetingRoomId = meetingRoomId;
        this.socket = null;
        this.localStream = null;
        this.peerConnections = new Map();
        this.participants = new Map();

        // WebRTC Configuration
        this.rtcConfig = {
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:stun1.l.google.com:19302' },
                { urls: 'stun:stun2.l.google.com:19302' }
            ]
        };

        // Media constraints
        this.mediaConstraints = {
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                frameRate: { ideal: 30 }
            },
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true
            }
        };

        // State tracking
        this.isAudioMuted = false;
        this.isVideoOff = false;
        this.isScreenSharing = false;
        this.isConnected = false;

        this.init();
    }

    async init() {
        try {
            // Initialize Socket.IO connection
            this.socket = io();
            this.setupSocketEvents();

            // Get user media
            await this.getUserMedia();

            // Join the meeting
            this.joinMeeting();

            console.log('WebRTC Client initialized successfully');
        } catch (error) {
            console.error('Failed to initialize WebRTC client:', error);
            this.showError('Failed to initialize video calling. Please check your camera and microphone permissions.');
        }
    }

    setupSocketEvents() {
        // Connection events
        this.socket.on('connect', () => {
            console.log('Connected to signaling server');
            this.isConnected = true;
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from signaling server');
            this.isConnected = false;
        });

        // Meeting events
        this.socket.on('meeting_joined', (data) => {
            console.log('Joined meeting:', data);
            this.handleMeetingJoined(data);
        });

        this.socket.on('participant_joined', (data) => {
            console.log('Participant joined:', data);
            this.handleParticipantJoined(data);
        });

        this.socket.on('participant_left', (data) => {
            console.log('Participant left:', data);
            this.handleParticipantLeft(data);
        });

        // WebRTC signaling events
        this.socket.on('webrtc_offer', (data) => {
            console.log('Received WebRTC offer from:', data.from_user_name);
            this.handleWebRTCOffer(data);
        });

        this.socket.on('webrtc_answer', (data) => {
            console.log('Received WebRTC answer from:', data.from_user_name);
            this.handleWebRTCAnswer(data);
        });

        this.socket.on('webrtc_ice_candidate', (data) => {
            console.log('Received ICE candidate from:', data.from_user_name);
            this.handleICECandidate(data);
        });

        // Media control events
        this.socket.on('participant_audio_changed', (data) => {
            this.updateParticipantAudioStatus(data.user_id, data.is_muted);
        });

        this.socket.on('participant_video_changed', (data) => {
            this.updateParticipantVideoStatus(data.user_id, data.is_video_off);
        });

        this.socket.on('participant_screen_share_started', (data) => {
            this.handleScreenShareStarted(data);
        });

        this.socket.on('participant_screen_share_stopped', (data) => {
            this.handleScreenShareStopped(data);
        });

        // Chat events
        this.socket.on('chat_message', (data) => {
            this.handleChatMessage(data);
        });

        // Admin forced actions
        this.socket.on('force_mute', (data) => {
            if (data.target_user_id === window.currentUserId) {
                this.forceMuteLocal();
                this.showNotification('You have been muted by the admin.');
            }
        });

        this.socket.on('force_kick', (data) => {
            if (data.target_user_id === window.currentUserId) {
                this.leaveMeeting();
                alert('You have been removed from the meeting by the admin.');
                window.location.href = '/';
            }
        });

        // Error handling
        this.socket.on('error', (data) => {
            console.error('Socket error:', data);
            this.showError(data.message);
        });
    }

    forceMuteLocal() {
        if (!this.isAudioMuted && this.localStream) {
            const audioTrack = this.localStream.getAudioTracks()[0];
            if (audioTrack) {
                audioTrack.enabled = false;
                this.isAudioMuted = true;

                // Update UI button
                const muteBtn = document.getElementById('muteBtn');
                if (muteBtn) {
                    const icon = muteBtn.querySelector('i');
                    icon.className = 'fas fa-microphone-slash';
                    muteBtn.style.background = '#ef4444';
                }

                // Notify server that I am now muted (state sync)
                this.socket.emit('toggle_audio', {
                    meeting_room_id: this.meetingRoomId,
                    is_muted: true
                });
            }
        }
    }

    async getUserMedia() {
        try {
            this.localStream = await navigator.mediaDevices.getUserMedia(this.mediaConstraints);

            // Display local video
            const localVideo = document.getElementById('localVideo');
            if (localVideo) {
                localVideo.srcObject = this.localStream;
                localVideo.muted = true; // Prevent echo
            }

            console.log('Got user media successfully');
            return this.localStream;
        } catch (error) {
            console.error('Error getting user media:', error);
            throw new Error('Could not access camera and microphone. Please grant permissions and try again.');
        }
    }

    joinMeeting() {
        if (this.socket && this.isConnected) {
            this.socket.emit('join_meeting', {
                meeting_room_id: this.meetingRoomId
            });
        }
    }

    leaveMeeting() {
        // Close all peer connections
        this.peerConnections.forEach((pc, userId) => {
            pc.close();
        });
        this.peerConnections.clear();

        // Stop local stream
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => track.stop());
        }

        // Leave meeting room
        if (this.socket) {
            this.socket.emit('leave_meeting', {
                meeting_room_id: this.meetingRoomId
            });
        }

        console.log('Left meeting');
    }

    async handleMeetingJoined(data) {
        console.log('Meeting joined successfully:', data);

        // Update UI with participant count
        this.updateParticipantCount(data.participant_count);

        // Add existing participants to list and create connections
        for (const participant of data.participants) {
            if (participant.user_id !== window.currentUserId) {
                this.addParticipantToList(participant.user_id, participant.user_name, participant.user_role);
                await this.createPeerConnection(participant.user_id, participant.user_name, participant.user_role, true);
            }
        }
    }

    async handleParticipantJoined(data) {
        console.log('New participant joined:', data);

        // Update participant count
        this.updateParticipantCount(data.participant_count);

        // Add to sidebar list
        this.addParticipantToList(data.user_id, data.user_name, data.user_role);

        // Create peer connection for new participant
        if (data.user_id !== window.currentUserId) {
            await this.createPeerConnection(data.user_id, data.user_name, data.user_role, false);
        }

        // Show notification
        this.showNotification(`${data.user_name} joined the meeting`);
    }

    handleParticipantLeft(data) {
        console.log('Participant left:', data);

        // Update participant count
        this.updateParticipantCount(data.participant_count);

        // Close peer connection
        if (this.peerConnections.has(data.user_id)) {
            this.peerConnections.get(data.user_id).close();
            this.peerConnections.delete(data.user_id);
        }

        // Remove participant from UI and List
        this.removeParticipantFromUI(data.user_id);
        this.removeParticipantFromList(data.user_id);

        // Show notification
        this.showNotification(`${data.user_name} left the meeting`);
    }

    async createPeerConnection(userId, userName, userRole, isInitiator) {
        try {
            const peerConnection = new RTCPeerConnection(this.rtcConfig);
            this.peerConnections.set(userId, peerConnection);

            // Store participant info with role
            this.participants.set(userId, { userName, userRole, stream: null });

            // Add local stream to peer connection
            if (this.localStream) {
                this.localStream.getTracks().forEach(track => {
                    peerConnection.addTrack(track, this.localStream);
                });
            }

            // Handle remote stream
            peerConnection.ontrack = (event) => {
                console.log('Received remote stream from:', userName, 'Role:', userRole);
                this.handleRemoteStream(userId, userName, event.streams[0], userRole);
            };

            // Handle ICE candidates
            peerConnection.onicecandidate = (event) => {
                if (event.candidate) {
                    this.socket.emit('webrtc_ice_candidate', {
                        meeting_room_id: this.meetingRoomId,
                        candidate: event.candidate
                    });
                }
            };

            // Handle connection state changes
            peerConnection.onconnectionstatechange = () => {
                console.log(`Connection state with ${userName}:`, peerConnection.connectionState);

                if (peerConnection.connectionState === 'connected') {
                    this.showNotification(`Connected to ${userName}`);
                } else if (peerConnection.connectionState === 'disconnected') {
                    this.showNotification(`Disconnected from ${userName}`);
                }
            };

            // If this is the initiator, create and send offer
            if (isInitiator) {
                const offer = await peerConnection.createOffer();
                await peerConnection.setLocalDescription(offer);

                this.socket.emit('webrtc_offer', {
                    meeting_room_id: this.meetingRoomId,
                    target_user_id: userId,
                    offer: offer
                });
            }

            console.log(`Created peer connection for ${userName} (${userRole})`);
        } catch (error) {
            console.error('Error creating peer connection:', error);
        }
    }

    // ... handleWebRTCOffer, handleWebRTCAnswer, handleICECandidate ...

    async handleWebRTCOffer(data) {
        try {
            const peerConnection = this.peerConnections.get(data.from_user_id);
            if (!peerConnection) {
                console.error('No peer connection found for offer');
                return;
            }

            await peerConnection.setRemoteDescription(data.offer);
            const answer = await peerConnection.createAnswer();
            await peerConnection.setLocalDescription(answer);

            this.socket.emit('webrtc_answer', {
                meeting_room_id: this.meetingRoomId,
                target_user_id: data.from_user_id,
                answer: answer
            });
        } catch (error) {
            console.error('Error handling WebRTC offer:', error);
        }
    }

    async handleWebRTCAnswer(data) {
        try {
            const peerConnection = this.peerConnections.get(data.from_user_id);
            if (!peerConnection) {
                console.error('No peer connection found for answer');
                return;
            }

            await peerConnection.setRemoteDescription(data.answer);
        } catch (error) {
            console.error('Error handling WebRTC answer:', error);
        }
    }

    async handleICECandidate(data) {
        try {
            const peerConnection = this.peerConnections.get(data.from_user_id);
            if (!peerConnection) {
                console.error('No peer connection found for ICE candidate');
                return;
            }

            await peerConnection.addIceCandidate(data.candidate);
        } catch (error) {
            console.error('Error handling ICE candidate:', error);
        }
    }

    handleRemoteStream(userId, userName, stream, userRole) {
        // Update participant stream info
        const ppt = this.participants.get(userId);
        if (ppt) ppt.stream = stream;

        // Check if admin -> Featured View
        if (userRole === 'admin') {
            this.renderFeaturedVideo(userId, userName, stream);
        } else {
            // Normal Grid View
            this.renderGridVideo(userId, userName, stream);
        }
    }

    renderFeaturedVideo(userId, userName, stream) {
        const featuredContainer = document.getElementById('featuredVideoContainer');
        const participantsGrid = document.getElementById('participantsGrid');
        const videoArea = document.querySelector('.video-area');
        const label = document.getElementById('featuredLabel');

        if (!featuredContainer) return;

        // Remove any existing video in featured container
        const existingVideo = featuredContainer.querySelector('video');
        if (existingVideo) existingVideo.remove();

        // Setup new video
        const videoElement = document.createElement('video');
        videoElement.id = `remoteVideo_${userId}`;
        videoElement.autoplay = true;
        videoElement.playsInline = true;
        videoElement.srcObject = stream;

        featuredContainer.appendChild(videoElement);
        if (label) label.textContent = `${userName} (Admin)`; // Update label with name

        // Show container and update layout
        featuredContainer.style.display = 'block';
        if (participantsGrid) participantsGrid.classList.add('has-featured');
        if (videoArea) videoArea.classList.add('view-featured');

        // Note: We don't add to grid if featured
        console.log(`Rendered ${userName} as featured admin`);
    }

    renderGridVideo(userId, userName, stream) {
        // Create or update video element for remote participant in GRID
        let videoElement = document.getElementById(`remoteVideo_${userId}`);

        // If it was previously featured, we might need to recreate it or move it (edge case if role changes, though unlikely dynamically)
        // But assuming ID uniqueness, if it exists, it might be in featured container?
        // Let's check parent.
        if (videoElement && videoElement.parentElement.classList.contains('featured-video-container')) {
            // It is in featured, but now we want grid? (Rare case).
            videoElement.remove();
            videoElement = null;
        }

        if (!videoElement) {
            // Create new video element
            const participantDiv = document.createElement('div');
            participantDiv.className = 'participant-video';
            participantDiv.id = `participant_${userId}`;

            videoElement = document.createElement('video');
            videoElement.id = `remoteVideo_${userId}`;
            videoElement.autoplay = true;
            videoElement.playsInline = true;
            videoElement.style.width = '100%';
            videoElement.style.height = '100%';
            videoElement.style.objectFit = 'cover';

            const nameLabel = document.createElement('div');
            nameLabel.className = 'participant-name';
            nameLabel.textContent = userName;

            participantDiv.appendChild(videoElement);
            participantDiv.appendChild(nameLabel);

            // Add to participants grid
            const participantsGrid = document.getElementById('participantsGrid');
            if (participantsGrid) {
                participantsGrid.appendChild(participantDiv);
            }
        }

        videoElement.srcObject = stream;
    }

    removeParticipantFromUI(userId) {
        // Check if featured
        const featuredContainer = document.getElementById('featuredVideoContainer');
        const videoElement = document.getElementById(`remoteVideo_${userId}`);

        if (videoElement && featuredContainer && featuredContainer.contains(videoElement)) {
            // It was the featured user
            videoElement.remove();
            featuredContainer.style.display = 'none';

            const participantsGrid = document.getElementById('participantsGrid');
            const videoArea = document.querySelector('.video-area');

            if (participantsGrid) participantsGrid.classList.remove('has-featured');
            if (videoArea) videoArea.classList.remove('view-featured');

        } else {
            // Check grid
            const participantDiv = document.getElementById(`participant_${userId}`);
            if (participantDiv) {
                participantDiv.remove();
            }
        }

        this.participants.delete(userId);
    }

    // Media Controls
    toggleAudio() {
        if (this.localStream) {
            const audioTrack = this.localStream.getAudioTracks()[0];
            if (audioTrack) {
                audioTrack.enabled = !audioTrack.enabled;
                this.isAudioMuted = !audioTrack.enabled;

                // Update UI
                const muteBtn = document.getElementById('muteBtn');
                if (muteBtn) {
                    const icon = muteBtn.querySelector('i');
                    if (this.isAudioMuted) {
                        icon.className = 'fas fa-microphone-slash';
                        muteBtn.style.background = '#ef4444';
                    } else {
                        icon.className = 'fas fa-microphone';
                        muteBtn.style.background = '#10b981';
                    }
                }

                // Notify other participants
                this.socket.emit('toggle_audio', {
                    meeting_room_id: this.meetingRoomId,
                    is_muted: this.isAudioMuted
                });

                console.log('Audio', this.isAudioMuted ? 'muted' : 'unmuted');
            }
        }
    }

    toggleVideo() {
        if (this.localStream) {
            const videoTrack = this.localStream.getVideoTracks()[0];
            if (videoTrack) {
                videoTrack.enabled = !videoTrack.enabled;
                this.isVideoOff = !videoTrack.enabled;

                // Update UI
                const videoBtn = document.getElementById('videoBtn');
                if (videoBtn) {
                    const icon = videoBtn.querySelector('i');
                    if (this.isVideoOff) {
                        icon.className = 'fas fa-video-slash';
                        videoBtn.style.background = '#ef4444';
                    } else {
                        icon.className = 'fas fa-video';
                        videoBtn.style.background = '#4f46e5';
                    }
                }

                // Notify other participants
                this.socket.emit('toggle_video', {
                    meeting_room_id: this.meetingRoomId,
                    is_video_off: this.isVideoOff
                });

                console.log('Video', this.isVideoOff ? 'turned off' : 'turned on');
            }
        }
    }

    async toggleScreenShare() {
        try {
            if (!this.isScreenSharing) {
                // Start screen sharing
                const screenStream = await navigator.mediaDevices.getDisplayMedia({
                    video: true,
                    audio: true
                });

                // Replace video track in all peer connections
                const videoTrack = screenStream.getVideoTracks()[0];
                this.peerConnections.forEach(async (pc) => {
                    const sender = pc.getSenders().find(s =>
                        s.track && s.track.kind === 'video'
                    );
                    if (sender) {
                        await sender.replaceTrack(videoTrack);
                    }
                });

                // Update local video
                const localVideo = document.getElementById('localVideo');
                if (localVideo) {
                    localVideo.srcObject = screenStream;
                }

                // Handle screen share end
                videoTrack.onended = () => {
                    this.stopScreenShare();
                };

                this.isScreenSharing = true;

                // Update UI
                const screenBtn = document.getElementById('screenBtn');
                if (screenBtn) {
                    screenBtn.style.background = '#f59e0b';
                }

                // Notify other participants
                this.socket.emit('screen_share_start', {
                    meeting_room_id: this.meetingRoomId
                });

                this.showNotification('Screen sharing started');
            } else {
                this.stopScreenShare();
            }
        } catch (error) {
            console.error('Error toggling screen share:', error);
            this.showError('Could not start screen sharing');
        }
    }

    async stopScreenShare() {
        try {
            // Get camera stream back
            const cameraStream = await navigator.mediaDevices.getUserMedia(this.mediaConstraints);

            // Replace screen track with camera track
            const videoTrack = cameraStream.getVideoTracks()[0];
            this.peerConnections.forEach(async (pc) => {
                const sender = pc.getSenders().find(s =>
                    s.track && s.track.kind === 'video'
                );
                if (sender) {
                    await sender.replaceTrack(videoTrack);
                }
            });

            // Update local video
            const localVideo = document.getElementById('localVideo');
            if (localVideo) {
                localVideo.srcObject = cameraStream;
            }

            // Update local stream reference
            this.localStream = cameraStream;
            this.isScreenSharing = false;

            // Update UI
            const screenBtn = document.getElementById('screenBtn');
            if (screenBtn) {
                screenBtn.style.background = '#10b981';
            }

            // Notify other participants
            this.socket.emit('screen_share_stop', {
                meeting_room_id: this.meetingRoomId
            });

            this.showNotification('Screen sharing stopped');
        } catch (error) {
            console.error('Error stopping screen share:', error);
        }
    }

    // Chat functionality
    sendChatMessage(message) {
        if (message.trim()) {
            this.socket.emit('chat_message', {
                meeting_room_id: this.meetingRoomId,
                message: message.trim()
            });
        }
    }

    handleChatMessage(data) {
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'chat-message';

            const timestamp = new Date(data.timestamp).toLocaleTimeString();
            messageDiv.innerHTML = `
                <div class="message-sender">${data.user_name} - ${timestamp}</div>
                <div class="message-content">${data.message}</div>
            `;

            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    // UI Helper functions
    updateParticipantCount(count) {
        const countElement = document.getElementById('participantCount');
        if (countElement) {
            countElement.textContent = count;
        }
    }

    updateParticipantAudioStatus(userId, isMuted) {
        const participantDiv = document.getElementById(`participant_${userId}`);
        const listItem = document.getElementById(`participant_list_${userId}`);

        // Update grid video indicator
        if (participantDiv) {
            // Add/remove muted indicator
            let mutedIndicator = participantDiv.querySelector('.muted-indicator');
            if (isMuted && !mutedIndicator) {
                mutedIndicator = document.createElement('div');
                mutedIndicator.className = 'muted-indicator';
                mutedIndicator.innerHTML = '<i class="fas fa-microphone-slash"></i>';
                participantDiv.appendChild(mutedIndicator);
            } else if (!isMuted && mutedIndicator) {
                mutedIndicator.remove();
            }
        }

        // Update list item status
        if (listItem) {
            const statusIcon = listItem.querySelector('.status-icon');
            if (statusIcon) {
                statusIcon.className = isMuted
                    ? 'status-icon status-muted'
                    : 'status-icon status-online';
            }
        }
    }

    updateParticipantVideoStatus(userId, isVideoOff) {
        const videoElement = document.getElementById(`remoteVideo_${userId}`);
        if (videoElement) {
            videoElement.style.display = isVideoOff ? 'none' : 'block';
        }
    }

    // Admin Controls
    kickParticipant(userId) {
        if (!confirm('Are you sure you want to remove this user from the meeting?')) return;

        this.socket.emit('admin_kick_user', {
            meeting_room_id: this.meetingRoomId,
            target_user_id: userId
        });
    }

    remoteToggleMute(userId) {
        this.socket.emit('admin_mute_user', {
            meeting_room_id: this.meetingRoomId,
            target_user_id: userId
        });
    }

    addParticipantToList(userId, userName, userRole) {
        const list = document.getElementById('participantsList');
        if (!list) return;

        const li = document.createElement('li');
        li.className = 'participant-item';
        li.id = `participant_list_${userId}`;

        let adminControls = '';
        if (window.currentUserRole === 'admin' && userId !== window.currentUserId) {
            adminControls = `
                <div class="participant-controls" style="display: flex; gap: 8px; margin-left: 8px;">
                     <button onclick="webrtcClient.remoteToggleMute(${userId})" class="admin-btn-mini" title="Toggle Mute" style="background: none; border: none; color: #ccc; cursor: pointer;">
                        <i class="fas fa-microphone-slash"></i>
                     </button>
                     <button onclick="webrtcClient.kickParticipant(${userId})" class="admin-btn-mini" title="Kick User" style="background: none; border: none; color: #ef4444; cursor: pointer;">
                        <i class="fas fa-user-times"></i>
                     </button>
                </div>
            `;
        }

        li.innerHTML = `
            <div class="participant-avatar">${userName[0].toUpperCase()}</div>
            <div class="participant-name">
                ${userName} 
                ${userRole === 'admin' ? '<span style="color: #f59e0b; font-size: 10px; border: 1px solid #f59e0b; padding: 1px 4px; border-radius: 4px; margin-left: 4px;">HOST</span>' : ''}
            </div>
            <div class="participant-status">
                <div class="status-icon status-online"></div>
            </div>
            ${adminControls}
        `;
        list.appendChild(li);
    }

    removeParticipantFromList(userId) {
        const li = document.getElementById(`participant_list_${userId}`);
        if (li) li.remove();
    }

    handleScreenShareStarted(data) {
        this.showNotification(`${data.user_name} started screen sharing`);
    }

    handleScreenShareStopped(data) {
        this.showNotification(`${data.user_name} stopped screen sharing`);
    }

    showNotification(message) {
        // Create toast notification
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(45, 45, 45, 0.9);
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            z-index: 10000;
            backdrop-filter: blur(10px);
            font-size: 14px;
        `;
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    showError(message) {
        console.error('WebRTC Error:', message);

        // Show error toast
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #ef4444;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            z-index: 10000;
            font-size: 14px;
        `;
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 5000);
    }
}

// Global WebRTC client instance
let webrtcClient = null;

// Initialize WebRTC when page loads
document.addEventListener('DOMContentLoaded', function () {
    // Check if we're on a meeting room page
    const meetingRoomId = window.meetingRoomId;
    if (meetingRoomId) {
        console.log('Initializing WebRTC for meeting:', meetingRoomId);
        webrtcClient = new WebRTCClient(meetingRoomId);
    }
});

// Global functions for meeting controls
function toggleMute() {
    if (webrtcClient) {
        webrtcClient.toggleAudio();
    }
}

function toggleVideo() {
    if (webrtcClient) {
        webrtcClient.toggleVideo();
    }
}

function toggleScreenShare() {
    if (webrtcClient) {
        webrtcClient.toggleScreenShare();
    }
}

function leaveMeeting() {
    if (confirm('Are you sure you want to leave the meeting?')) {
        if (webrtcClient) {
            webrtcClient.leaveMeeting();
        }
        // Redirect to dashboard
        window.location.href = `/${window.currentUserRole}`;
    }
}

function handleChatInput(event) {
    if (event.key === 'Enter' && event.target.value.trim()) {
        if (webrtcClient) {
            webrtcClient.sendChatMessage(event.target.value.trim());
        }
        event.target.value = '';
    }
}