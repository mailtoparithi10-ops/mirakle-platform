"""
Rate Limiting Configuration for InnoBridge Platform
Defines rate limits for different endpoints and user types
"""

# Global rate limits (applied to all routes unless overridden)
GLOBAL_RATE_LIMITS = [
    "200 per day",
    "50 per hour"
]

# Authentication endpoints
AUTH_RATE_LIMITS = {
    "login": "5 per minute",
    "register": "3 per minute",
    "logout": "10 per minute",
    "password_reset": "3 per hour",
    "google_oauth": "10 per hour"
}

# API endpoints
API_RATE_LIMITS = {
    "default": "100 per hour",
    "read": "200 per hour",
    "write": "50 per hour",
    "delete": "20 per hour"
}

# File upload endpoints
UPLOAD_RATE_LIMITS = {
    "logo": "10 per hour",
    "pitch_deck": "10 per hour",
    "poster": "5 per hour",
    "profile_picture": "10 per hour"
}

# Meeting endpoints
MEETING_RATE_LIMITS = {
    "create": "10 per hour",
    "join": "50 per hour",
    "list": "100 per hour"
}

# Referral endpoints
REFERRAL_RATE_LIMITS = {
    "create": "20 per hour",
    "generate_link": "10 per hour",
    "track_click": "1000 per hour"  # Higher limit for tracking
}

# Admin endpoints (more lenient)
ADMIN_RATE_LIMITS = {
    "default": "500 per hour",
    "bulk_operations": "50 per hour"
}

# Exempted IPs (for testing, monitoring, etc.)
EXEMPTED_IPS = [
    "127.0.0.1",  # Localhost
    # Add production monitoring IPs here
]

# Custom error messages
RATE_LIMIT_MESSAGES = {
    "default": "Rate limit exceeded. Please try again later.",
    "login": "Too many login attempts. Please wait a minute and try again.",
    "register": "Too many registration attempts. Please wait a minute and try again.",
    "api": "API rate limit exceeded. Please slow down your requests.",
    "upload": "File upload limit exceeded. Please wait before uploading more files."
}

def get_rate_limit_message(endpoint_type="default"):
    """Get custom rate limit message for endpoint type"""
    return RATE_LIMIT_MESSAGES.get(endpoint_type, RATE_LIMIT_MESSAGES["default"])

def is_ip_exempted(ip_address):
    """Check if IP is exempted from rate limiting"""
    return ip_address in EXEMPTED_IPS