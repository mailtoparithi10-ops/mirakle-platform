// Referral Link Generation and QR Code System

class ReferralLinkManager {
    constructor() {
        this.currentReferral = null;
    }

    // Show referral link modal for an opportunity
    async showReferralModal(opportunityId, opportunityTitle) {
        try {
            // Generate the referral link
            const response = await fetch('/api/referrals/generate-link', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ opportunity_id: opportunityId })
            });

            const data = await response.json();

            if (data.success) {
                this.currentReferral = data;
                this.displayReferralModal(data, opportunityTitle);
            } else {
                this.showError(data.error || 'Failed to generate referral link');
            }
        } catch (error) {
            console.error('Error generating referral link:', error);
            this.showError('Failed to generate referral link');
        }
    }

    // Display the modal with link and QR code
    displayReferralModal(data, opportunityTitle) {
        const modal = document.createElement('div');
        modal.className = 'referral-modal-overlay';
        modal.innerHTML = `
            <div class="referral-modal">
                <div class="referral-modal-header">
                    <h2><i class="fas fa-share-alt"></i> Share Opportunity</h2>
                    <button class="close-btn" onclick="this.closest('.referral-modal-overlay').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>

                <div class="referral-modal-body">
                    <div class="opportunity-info">
                        <h3>${opportunityTitle}</h3>
                        <p class="text-muted">Share this opportunity with startups using the link or QR code below</p>
                    </div>

                    <div class="referral-tabs">
                        <button class="tab-btn active" onclick="switchReferralTab('link')">
                            <i class="fas fa-link"></i> Shareable Link
                        </button>
                        <button class="tab-btn" onclick="switchReferralTab('qr')">
                            <i class="fas fa-qrcode"></i> QR Code
                        </button>
                    </div>

                    <!-- Link Tab -->
                    <div id="linkTab" class="tab-content active">
                        <div class="link-container">
                            <div class="link-box">
                                <input type="text" id="referralLink" value="${data.join_url}" readonly>
                                <button class="copy-btn" onclick="copyReferralLink()">
                                    <i class="fas fa-copy"></i> Copy
                                </button>
                            </div>
                            <p class="link-info">
                                <i class="fas fa-info-circle"></i>
                                Startups must login to access this opportunity. You'll be able to track who clicks and applies.
                            </p>
                        </div>

                        <div class="share-buttons">
                            <button class="share-btn whatsapp" onclick="shareViaWhatsApp('${data.join_url}', '${opportunityTitle}')">
                                <i class="fab fa-whatsapp"></i> WhatsApp
                            </button>
                            <button class="share-btn email" onclick="shareViaEmail('${data.join_url}', '${opportunityTitle}')">
                                <i class="fas fa-envelope"></i> Email
                            </button>
                            <button class="share-btn telegram" onclick="shareViaTelegram('${data.join_url}', '${opportunityTitle}')">
                                <i class="fab fa-telegram"></i> Telegram
                            </button>
                        </div>
                    </div>

                    <!-- QR Code Tab -->
                    <div id="qrTab" class="tab-content">
                        <div class="qr-container">
                            <div id="qrcode" class="qr-code-display"></div>
                            <p class="qr-info">
                                <i class="fas fa-mobile-alt"></i>
                                Scan this QR code with a mobile device to access the opportunity
                            </p>
                            <button class="download-btn" onclick="downloadQRCode('${opportunityTitle}')">
                                <i class="fas fa-download"></i> Download QR Code
                            </button>
                        </div>
                    </div>

                    <!-- Tracking Info -->
                    <div class="tracking-info">
                        <h4><i class="fas fa-chart-line"></i> Tracking</h4>
                        <div class="tracking-stats" id="trackingStats">
                            <div class="stat-item">
                                <div class="stat-value" id="clickCount">0</div>
                                <div class="stat-label">Clicks</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value" id="viewCount">0</div>
                                <div class="stat-label">Views</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value" id="applyCount">0</div>
                                <div class="stat-label">Applications</div>
                            </div>
                        </div>
                        <button class="view-details-btn" onclick="viewReferralDetails(${data.referral_id})">
                            View Detailed Analytics
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Generate QR Code
        this.generateQRCode(data.join_url);

        // Load initial stats
        this.loadReferralStats(data.referral_id);

        // Auto-refresh stats every 10 seconds
        this.statsInterval = setInterval(() => {
            this.loadReferralStats(data.referral_id);
        }, 10000);
    }

    // Generate QR Code using QRCode.js library
    generateQRCode(url) {
        const qrContainer = document.getElementById('qrcode');
        if (qrContainer && typeof QRCode !== 'undefined') {
            qrContainer.innerHTML = ''; // Clear previous QR code
            new QRCode(qrContainer, {
                text: url,
                width: 256,
                height: 256,
                colorDark: "#000000",
                colorLight: "#ffffff",
                correctLevel: QRCode.CorrectLevel.H
            });
        } else {
            // Fallback: Use Google Charts API
            qrContainer.innerHTML = `
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=256x256&data=${encodeURIComponent(url)}" 
                     alt="QR Code" 
                     style="max-width: 100%;">
            `;
        }
    }

    // Load referral statistics
    async loadReferralStats(referralId) {
        try {
            const response = await fetch(`/api/referrals/link-stats/${referralId}`);
            const data = await response.json();

            if (data.success) {
                document.getElementById('clickCount').textContent = data.stats.total_clicks;
                document.getElementById('viewCount').textContent = data.stats.viewed_opportunity;
                document.getElementById('applyCount').textContent = data.stats.applied;
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    showError(message) {
        alert(message); // Replace with better error handling
    }
}

// Global instance
const referralManager = new ReferralLinkManager();

// Tab switching
function switchReferralTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    if (tab === 'link') {
        document.querySelector('.tab-btn:first-child').classList.add('active');
        document.getElementById('linkTab').classList.add('active');
    } else {
        document.querySelector('.tab-btn:last-child').classList.add('active');
        document.getElementById('qrTab').classList.add('active');
    }
}

// Copy link to clipboard
function copyReferralLink() {
    const linkInput = document.getElementById('referralLink');
    linkInput.select();
    document.execCommand('copy');

    // Show feedback
    const copyBtn = document.querySelector('.copy-btn');
    const originalText = copyBtn.innerHTML;
    copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
    copyBtn.style.background = '#10b981';

    setTimeout(() => {
        copyBtn.innerHTML = originalText;
        copyBtn.style.background = '';
    }, 2000);
}

// Share via WhatsApp
function shareViaWhatsApp(url, title) {
    const text = `Check out this opportunity: ${title}\n\n${url}`;
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank');
}

// Share via Email
function shareViaEmail(url, title) {
    const subject = `Opportunity: ${title}`;
    const body = `I thought you might be interested in this opportunity:\n\n${title}\n\n${url}`;
    window.location.href = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
}

// Share via Telegram
function shareViaTelegram(url, title) {
    const text = `Check out this opportunity: ${title}`;
    window.open(`https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`, '_blank');
}

// Download QR Code
function downloadQRCode(opportunityTitle) {
    const qrCanvas = document.querySelector('#qrcode canvas');
    if (qrCanvas) {
        const link = document.createElement('a');
        link.download = `${opportunityTitle.replace(/[^a-z0-9]/gi, '_')}_QR.png`;
        link.href = qrCanvas.toDataURL();
        link.click();
    } else {
        // Fallback for image-based QR
        const qrImg = document.querySelector('#qrcode img');
        if (qrImg) {
            const link = document.createElement('a');
            link.download = `${opportunityTitle.replace(/[^a-z0-9]/gi, '_')}_QR.png`;
            link.href = qrImg.src;
            link.click();
        }
    }
}

// View detailed analytics
function viewReferralDetails(referralId) {
    window.location.href = `/connector/referrals/${referralId}`;
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Referral Link Manager initialized');
});