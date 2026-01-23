// Meeting functionality for user dashboards

class MeetingInbox {
    constructor() {
        this.meetings = [];
        this.init();
    }

    async init() {
        await this.loadUserMeetings();
        this.renderMeetingInbox();
        this.startPolling();
    }

    async loadUserMeetings() {
        try {
            const response = await fetch('/api/meetings/my-meetings');
            
            // Handle authentication redirect
            if (response.redirected || response.status === 401 || response.status === 403) {
                console.log('User not authenticated for meetings');
                this.meetings = { upcoming: [], past: [] };
                return;
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.meetings = {
                    upcoming: data.upcoming_meetings || [],
                    past: data.past_meetings || []
                };
            } else {
                console.log('Failed to load meetings:', data.error);
                this.meetings = { upcoming: [], past: [] };
            }
        } catch (error) {
            console.error('Error loading meetings:', error);
            this.meetings = { upcoming: [], past: [] };
        }
    }

    renderMeetingInbox() {
        const container = document.getElementById('meetingInbox');
        if (!container) {
            console.log('Meeting inbox container not found');
            return;
        }

        const upcomingMeetings = this.meetings.upcoming || [];
        const hasUpcoming = upcomingMeetings.length > 0;
        
        console.log('Rendering meeting inbox:', { upcomingMeetings: upcomingMeetings.length, hasUpcoming });

        container.innerHTML = `
            <div class="inbox-header">
                <h3><i class="fas fa-video"></i> Meeting Inbox</h3>
                ${hasUpcoming ? `<span class="meeting-badge">${upcomingMeetings.length}</span>` : ''}
            </div>
            <div class="meeting-list">
                ${hasUpcoming ? this.renderUpcomingMeetings(upcomingMeetings) : this.renderEmptyState()}
            </div>
        `;
    }

    renderUpcomingMeetings(meetings) {
        return meetings.slice(0, 3).map(meeting => {
            const meetingDate = new Date(meeting.scheduled_at);
            const isToday = this.isToday(meetingDate);
            const timeUntil = this.getTimeUntil(meetingDate);
            
            return `
                <div class="meeting-item ${isToday ? 'meeting-today' : ''}" onclick="viewMeeting('${meeting.meeting_room_id}')">
                    <div class="meeting-icon">
                        <i class="fas fa-video"></i>
                    </div>
                    <div class="meeting-details">
                        <div class="meeting-title">${meeting.title}</div>
                        <div class="meeting-time">
                            ${meetingDate.toLocaleDateString()} at ${meetingDate.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                        </div>
                        <div class="meeting-meta">
                            <span class="time-until">${timeUntil}</span>
                            <span class="participant-count">${meeting.participant_count} participants</span>
                        </div>
                    </div>
                    <div class="meeting-actions">
                        <button class="join-btn" onclick="event.stopPropagation(); joinMeeting('${meeting.meeting_room_id}')">
                            <i class="fas fa-sign-in-alt"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }

    renderEmptyState() {
        return `
            <div class="empty-meetings">
                <i class="fas fa-calendar-alt"></i>
                <p>No upcoming meetings</p>
                <small>You'll see your scheduled meetings here</small>
            </div>
        `;
    }

    isToday(date) {
        const today = new Date();
        return date.toDateString() === today.toDateString();
    }

    getTimeUntil(meetingDate) {
        const now = new Date();
        const diff = meetingDate - now;
        
        if (diff < 0) return 'Started';
        
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        
        if (hours > 24) {
            const days = Math.floor(hours / 24);
            return `in ${days} day${days > 1 ? 's' : ''}`;
        } else if (hours > 0) {
            return `in ${hours}h ${minutes}m`;
        } else if (minutes > 0) {
            return `in ${minutes}m`;
        } else {
            return 'Starting now';
        }
    }

    startPolling() {
        // Refresh meetings every 5 minutes
        setInterval(() => {
            this.loadUserMeetings().then(() => {
                this.renderMeetingInbox();
            });
        }, 5 * 60 * 1000);
    }
}

// Global functions for meeting actions
function viewMeeting(meetingRoomId) {
    window.location.href = `/meeting/join/${meetingRoomId}`;
}

function joinMeeting(meetingRoomId) {
    window.location.href = `/meeting/join/${meetingRoomId}`;
}

// Initialize meeting inbox when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, checking for meeting inbox...');
    const meetingInboxElement = document.getElementById('meetingInbox');
    if (meetingInboxElement) {
        console.log('Meeting inbox element found, initializing...');
        new MeetingInbox();
    } else {
        console.log('Meeting inbox element not found');
    }
});