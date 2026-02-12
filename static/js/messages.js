// Messages JavaScript
let currentThreadId = null;
let currentRecipientId = null;
let threads = [];
let messages = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadThreads();
    setupEventListeners();
    
    // Auto-refresh threads every 30 seconds
    setInterval(loadThreads, 30000);
    
    // Auto-refresh current conversation every 10 seconds
    setInterval(() => {
        if (currentThreadId) {
            loadThread(currentThreadId, false);
        }
    }, 10000);
});

function setupEventListeners() {
    // Search functionality
    document.getElementById('searchInput').addEventListener('input', (e) => {
        filterThreads(e.target.value);
    });
    
    // Send message form
    document.getElementById('composeForm').addEventListener('submit', (e) => {
        e.preventDefault();
        sendMessage();
    });
    
    // Auto-resize textarea
    const messageInput = document.getElementById('messageInput');
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        messageInput.style.height = messageInput.scrollHeight + 'px';
    });
    
    // Send on Enter (Shift+Enter for new line)
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

async function loadThreads() {
    try {
        const response = await fetch('/api/messages/threads');
        const data = await response.json();
        
        if (data.success) {
            threads = data.threads;
            renderThreads(threads);
        }
    } catch (error) {
        console.error('Error loading threads:', error);
        showError('Failed to load conversations');
    }
}

function renderThreads(threadsToRender) {
    const threadsList = document.getElementById('threadsList');
    
    if (threadsToRender.length === 0) {
        threadsList.innerHTML = `
            <div class="empty-state" style="padding: 2rem;">
                <i class="fas fa-inbox"></i>
                <p>No conversations yet</p>
            </div>
        `;
        return;
    }
    
    threadsList.innerHTML = threadsToRender.map(thread => {
        const otherUser = thread.other_user;
        const latestMsg = thread.latest_message;
        const isUnread = thread.unread_count > 0;
        const isActive = thread.thread_id === currentThreadId;
        
        // Format time
        const msgTime = new Date(latestMsg.created_at);
        const timeStr = formatMessageTime(msgTime);
        
        // Get avatar
        const avatarContent = otherUser.profile_pic 
            ? `<img src="${otherUser.profile_pic}" alt="${otherUser.name}">`
            : otherUser.name.charAt(0).toUpperCase();
        
        return `
            <div class="thread-item ${isActive ? 'active' : ''}" 
                 onclick="selectThread('${thread.thread_id}', ${otherUser.id})">
                <div class="thread-header">
                    <div class="thread-user">
                        <div class="thread-avatar">${avatarContent}</div>
                        <div class="thread-info">
                            <div class="thread-name">${otherUser.name}</div>
                            <div class="thread-time">${timeStr}</div>
                        </div>
                    </div>
                    ${isUnread ? `<span class="unread-badge">${thread.unread_count}</span>` : ''}
                </div>
                <div class="thread-preview ${isUnread ? 'unread' : ''}">
                    ${latestMsg.body.substring(0, 60)}${latestMsg.body.length > 60 ? '...' : ''}
                </div>
            </div>
        `;
    }).join('');
}

function filterThreads(query) {
    if (!query) {
        renderThreads(threads);
        return;
    }
    
    const filtered = threads.filter(thread => {
        const userName = thread.other_user.name.toLowerCase();
        const messageBody = thread.latest_message.body.toLowerCase();
        const searchQuery = query.toLowerCase();
        
        return userName.includes(searchQuery) || messageBody.includes(searchQuery);
    });
    
    renderThreads(filtered);
}

async function selectThread(threadId, recipientId) {
    currentThreadId = threadId;
    currentRecipientId = recipientId;
    
    await loadThread(threadId);
    
    // Update active state
    document.querySelectorAll('.thread-item').forEach(item => {
        item.classList.remove('active');
    });
    event.currentTarget.classList.add('active');
}

async function loadThread(threadId, scrollToBottom = true) {
    try {
        const response = await fetch(`/api/messages/thread/${threadId}`);
        const data = await response.json();
        
        if (data.success) {
            messages = data.messages;
            renderMessages(messages, scrollToBottom);
            
            // Show conversation header and compose area
            const thread = threads.find(t => t.thread_id === threadId);
            if (thread) {
                updateConversationHeader(thread.other_user);
            }
            
            document.getElementById('conversationHeader').style.display = 'flex';
            document.getElementById('composeArea').style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading thread:', error);
        showError('Failed to load messages');
    }
}

function updateConversationHeader(user) {
    const avatarContent = user.profile_pic 
        ? `<img src="${user.profile_pic}" alt="${user.name}">`
        : user.name.charAt(0).toUpperCase();
    
    document.getElementById('headerAvatar').innerHTML = avatarContent;
    document.getElementById('headerName').textContent = user.name;
    document.getElementById('headerRole').textContent = `${user.role} ${user.company ? `at ${user.company}` : ''}`;
}

function renderMessages(messagesToRender, scrollToBottom = true) {
    const messagesArea = document.getElementById('messagesArea');
    
    if (messagesToRender.length === 0) {
        messagesArea.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-comment-dots"></i>
                <h3>Start the conversation</h3>
                <p>Send your first message below</p>
            </div>
        `;
        return;
    }
    
    messagesArea.innerHTML = messagesToRender.map(msg => {
        const isSent = msg.sender_id === parseInt(document.body.dataset.userId || '0');
        const msgTime = new Date(msg.created_at);
        const timeStr = formatMessageTime(msgTime);
        
        const avatarContent = msg.sender_profile_pic 
            ? `<img src="${msg.sender_profile_pic}" alt="${msg.sender_name}">`
            : msg.sender_name.charAt(0).toUpperCase();
        
        return `
            <div class="message ${isSent ? 'sent' : 'received'}">
                <div class="message-avatar">${avatarContent}</div>
                <div class="message-content">
                    <div class="message-bubble">
                        <div class="message-text">${escapeHtml(msg.body)}</div>
                    </div>
                    <div class="message-time">${timeStr}</div>
                </div>
            </div>
        `;
    }).join('');
    
    if (scrollToBottom) {
        messagesArea.scrollTop = messagesArea.scrollHeight;
    }
}

async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const body = messageInput.value.trim();
    
    if (!body || !currentRecipientId) return;
    
    // Disable input while sending
    messageInput.disabled = true;
    sendButton.disabled = true;
    
    try {
        const response = await fetch('/api/messages/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                recipient_id: currentRecipientId,
                body: body,
                thread_id: currentThreadId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Clear input
            messageInput.value = '';
            messageInput.style.height = 'auto';
            
            // Reload thread to show new message
            await loadThread(currentThreadId);
            
            // Reload threads to update preview
            await loadThreads();
        } else {
            showError(data.message || 'Failed to send message');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        showError('Failed to send message');
    } finally {
        messageInput.disabled = false;
        sendButton.disabled = false;
        messageInput.focus();
    }
}

function formatMessageTime(date) {
    const now = new Date();
    const diff = now - date;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (seconds < 60) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showError(message) {
    // Simple error notification (you can enhance this)
    alert(message);
}

// Export functions for external use
window.MessagingApp = {
    loadThreads,
    selectThread,
    sendMessage
};
