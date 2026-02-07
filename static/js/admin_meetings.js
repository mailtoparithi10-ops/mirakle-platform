// Admin Meeting Management
async function loadMeetings() {
    const container = document.getElementById('meetingsList');
    if (!container) return;

    container.innerHTML = '<div class="loading" style="margin: 20px auto;"></div><p style="text-align: center;">Loading meetings...</p>';

    try {
        const response = await fetch('/api/meetings/');
        const data = await response.json();

        if (data.success && data.meetings) {
            renderMeetings(data.meetings);
        } else {
            container.innerHTML = `<p style="text-align: center; padding: 20px; color: #64748b;">${data.error || 'Failed to load meetings'}</p>`;
        }
    } catch (error) {
        console.error('Error loading meetings:', error);
        container.innerHTML = '<p style="text-align: center; color: #ef4444; padding: 20px;">Failed to load meetings. Please check your connection.</p>';
    }
}

async function loadMeetingStats() {
    try {
        const response = await fetch('/api/meetings/stats');
        const data = await response.json();

        if (data.success && data.stats) {
            const stats = data.stats;
            if (document.getElementById('totalMeetings')) document.getElementById('totalMeetings').textContent = stats.total_meetings;
            if (document.getElementById('upcomingMeetings')) document.getElementById('upcomingMeetings').textContent = stats.upcoming_meetings;
            if (document.getElementById('totalParticipants')) document.getElementById('totalParticipants').textContent = stats.total_participants;
        }
    } catch (error) {
        console.error('Error loading meeting stats:', error);
    }
}

function renderMeetings(meetings) {
    const container = document.getElementById('meetingsList');
    if (!container) return;

    if (!meetings || meetings.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 40px;">
                <i class="fas fa-video-slash" style="font-size: 48px; color: #cbd5e1; margin-bottom: 1rem;"></i>
                <p style="color: #64748b;">No meetings found</p>
                <button onclick="showCreateMeetingModal()" class="admin-btn primary" style="margin-top: 1rem;">Create One Now</button>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <div class="table-responsive">
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>Meeting Info</th>
                        <th>Access</th>
                        <th>Stats</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${meetings.map(m => {
        const date = new Date(m.scheduled_at);
        const dateStr = date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const statusClass = m.status === 'scheduled' ? 'status-scheduled' : (m.status === 'in_progress' ? 'status-active' : 'status-completed');

        return `
                            <tr>
                                <td>
                                    <div style="font-weight: 700; color: #1e293b;">${m.title}</div>
                                    <div style="font-size: 11px; color: #64748b;">${dateStr} (${m.duration_minutes}m)</div>
                                    <div style="font-size: 10px; color: #94a3b8; font-family: monospace;">ID: ${m.meeting_room_id}</div>
                                </td>
                                <td>
                                    <span class="badge-soft ${m.access_type === 'all_users' ? 'blue' : 'gold'}" style="font-size: 10px; padding: 2px 6px;">
                                        ${m.access_type.replace('_', ' ').toUpperCase()}
                                    </span>
                                </td>
                                <td>
                                    <div style="font-size: 12px; color: #475569;">
                                        <i class="fas fa-users"></i> ${m.participant_count} / ${m.max_participants}
                                    </div>
                                </td>
                                <td>
                                    <span class="status-pill ${statusClass}">${m.status.toUpperCase()}</span>
                                </td>
                                <td>
                                    <div style="display: flex; gap: 8px;">
                                        <button class="btn-icon" onclick="joinMeeting('${m.meeting_room_id}')" title="Join Meeting">
                                            <i class="fas fa-sign-in-alt"></i>
                                        </button>
                                        <button class="btn-icon" onclick="copyMeetingLink('${m.meeting_room_id}')" title="Copy Link">
                                            <i class="fas fa-link"></i>
                                        </button>
                                        <button class="btn-icon danger" onclick="deleteMeeting(${m.id})" title="Delete">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        `;
    }).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function showCreateMeetingModal() {
    const modal = document.createElement('div');
    modal.className = 'modal-backdrop';
    modal.innerHTML = `
        <div class="modal-card" style="width: 100%; max-width: 600px; max-height: 90vh; overflow-y: auto;">
            <div class="modal-header">
                <h3 class="modal-title">Create Real-Time Meeting</h3>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-body">
                <form id="createMeetingForm">
                    <div class="form-group" style="margin-bottom: 1.5rem;">
                        <label class="form-label">Meeting Title *</label>
                        <input type="text" name="title" class="form-input" required placeholder="e.g. Q1 Strategic Planning">
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem;">
                        <div class="form-group">
                            <label class="form-label">Scheduled Time *</label>
                            <input type="datetime-local" name="scheduled_at" class="form-input" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Duration (minutes)</label>
                            <input type="number" name="duration_minutes" class="form-input" value="60">
                        </div>
                    </div>

                    <div class="form-group" style="margin-bottom: 1.5rem;">
                        <label class="form-label">Access Type *</label>
                        <select name="access_type" class="form-select" required onchange="handleAccessTypeChange(this.value)">
                            <option value="all_users">All Platform Users</option>
                            <option value="startup_only">Startups Only</option>
                            <option value="corporate_only">Corporates Only</option>
                            <option value="connector_only">Enablers Only</option>
                            <option value="specific_users">Specific Users</option>
                        </select>
                    </div>

                    <div id="specificUsersSection" style="display: none; margin-bottom: 1.5rem; background: #f8fafc; padding: 1rem; border-radius: 8px;">
                        <label class="form-label">Select Users</label>
                        <div id="usersCheckboxes" style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; max-height: 150px; overflow-y: auto;">
                            <!-- Populated by JS -->
                            <div class="loading"></div>
                        </div>
                    </div>

                    <div class="form-group" style="margin-bottom: 1.5rem;">
                        <label class="form-label">Description (optional)</label>
                        <textarea name="description" class="form-input" rows="3" placeholder="Meeting agenda..."></textarea>
                    </div>

                    <div style="background: #f1f5f9; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
                        <h4 style="font-size: 0.9rem; font-weight: 700; margin-bottom: 0.75rem;">Meeting Controls</h4>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
                            <label style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; cursor: pointer;">
                                <input type="checkbox" name="video_enabled" checked> Enable Video
                            </label>
                            <label style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; cursor: pointer;">
                                <input type="checkbox" name="audio_enabled" checked> Enable Audio
                            </label>
                            <label style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; cursor: pointer;">
                                <input type="checkbox" name="screen_sharing_enabled" checked> Screen Sharing
                            </label>
                            <label style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; cursor: pointer;">
                                <input type="checkbox" name="chat_enabled" checked> Enable Chat
                            </label>
                        </div>
                    </div>

                    <div class="modal-footer" style="padding: 0; border: none;">
                        <button type="button" class="admin-btn" onclick="closeModal()">Cancel</button>
                        <button type="submit" class="admin-btn primary">Create Meeting</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    document.body.appendChild(modal);

    // Initial setup for time (default to now + 30 mins)
    const now = new Date();
    now.setMinutes(now.getMinutes() + 30);
    now.setSeconds(0, 0);
    const timeInput = modal.querySelector('input[name="scheduled_at"]');
    timeInput.value = now.toISOString().slice(0, 16);

    // Form submission
    const form = document.getElementById('createMeetingForm');
    form.addEventListener('submit', handleCreateMeeting);
}

async function handleAccessTypeChange(value) {
    const section = document.getElementById('specificUsersSection');
    if (value === 'specific_users') {
        section.style.display = 'block';
        await loadUsersForCheckboxes();
    } else {
        section.style.display = 'none';
    }
}

async function loadUsersForCheckboxes() {
    const container = document.getElementById('usersCheckboxes');
    try {
        const response = await fetch('/api/admin/users');
        const users = await response.json();

        container.innerHTML = users.map(u => `
            <label style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.8rem; cursor: pointer;">
                <input type="checkbox" name="specific_user_ids" value="${u.id}"> 
                <span title="${u.email}">${u.name || u.username}</span>
            </label>
        `).join('');
    } catch (error) {
        container.innerHTML = '<p style="color:red; font-size:0.7rem;">Failed to load users</p>';
    }
}

async function handleCreateMeeting(e) {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';

    const formData = new FormData(e.target);
    const data = {
        title: formData.get('title'),
        scheduled_at: formData.get('scheduled_at'),
        duration_minutes: parseInt(formData.get('duration_minutes')),
        access_type: formData.get('access_type'),
        description: formData.get('description'),
        video_enabled: formData.has('video_enabled'),
        audio_enabled: formData.has('audio_enabled'),
        screen_sharing_enabled: formData.has('screen_sharing_enabled'),
        chat_enabled: formData.has('chat_enabled'),
        specific_user_ids: Array.from(e.target.querySelectorAll('input[name="specific_user_ids"]:checked')).map(cb => parseInt(cb.value))
    };

    try {
        const response = await fetch('/api/meetings/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();

        if (result.success) {
            showToast('Meeting created successfully!', 'success');
            closeModal();
            loadMeetings();
            loadMeetingStats();
        } else {
            showToast(result.error || 'Failed to create meeting', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Connection error', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Create Meeting';
    }
}

async function deleteMeeting(id) {
    if (!confirm('Are you sure you want to delete this meeting? This will notify all participants.')) return;

    try {
        const response = await fetch(`/api/meetings/${id}`, { method: 'DELETE' });
        const data = await response.json();

        if (data.success) {
            showToast('Meeting deleted successfully', 'success');
            loadMeetings();
            loadMeetingStats();
        } else {
            showToast(data.error || 'Failed to delete meeting', 'error');
        }
    } catch (error) {
        showToast('Connection error', 'error');
    }
}

function copyMeetingLink(meetingRoomId) {
    const url = window.location.origin + `/meeting/join/${meetingRoomId}`;
    navigator.clipboard.writeText(url).then(() => {
        showToast('Meeting join link copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Copy failed:', err);
    });
}

function closeModal() {
    const modal = document.querySelector('.modal-backdrop');
    if (modal) modal.remove();
}

function filterMeetings(filter) {
    document.querySelectorAll('.filter-tab').forEach(tab => tab.classList.remove('active'));
    event.target.classList.add('active');

    // In a real app, you might fetch filtered data or filter locally
    loadMeetings(); // For now, just reload all
}
