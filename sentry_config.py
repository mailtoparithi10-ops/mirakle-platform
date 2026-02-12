"""
Sentry Configuration and Initialization
Handles error tracking and performance monitoring setup
"""

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import logging


def init_sentry(app):
    """
    Initialize Sentry for error tracking and performance monitoring
    
    Args:
        app: Flask application instance
    """
    
    sentry_dsn = app.config.get('SENTRY_DSN')
    
    # Only initialize if DSN is provided
    if not sentry_dsn:
        app.logger.info("Sentry DSN not configured. Skipping Sentry initialization.")
        return
    
    environment = app.config.get('SENTRY_ENVIRONMENT', 'development')
    traces_sample_rate = app.config.get('SENTRY_TRACES_SAMPLE_RATE', 0.1)
    profiles_sample_rate = app.config.get('SENTRY_PROFILES_SAMPLE_RATE', 0.1)
    
    # Configure logging integration
    logging_integration = LoggingIntegration(
        level=logging.INFO,        # Capture info and above as breadcrumbs
        event_level=logging.ERROR  # Send errors as events
    )
    
    # Initialize Sentry
    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=environment,
        
        # Integrations
        integrations=[
            FlaskIntegration(),
            SqlalchemyIntegration(),
            logging_integration,
        ],
        
        # Performance Monitoring
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate,
        
        # Additional options
        send_default_pii=False,  # Don't send personally identifiable information
        attach_stacktrace=True,
        
        # Release tracking (optional - set via environment variable)
        release=app.config.get('SENTRY_RELEASE'),
        
        # Before send hook for filtering
        before_send=before_send_filter,
    )
    
    app.logger.info(f"Sentry initialized for environment: {environment}")


def before_send_filter(event, hint):
    """
    Filter events before sending to Sentry
    Can be used to:
    - Remove sensitive data
    - Filter out certain errors
    - Add custom context
    """
    
    # Example: Filter out 404 errors
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']
        if isinstance(exc_value, KeyError):
            # You might want to ignore certain KeyErrors
            pass
    
    # Example: Remove sensitive data from request
    if 'request' in event:
        request = event['request']
        if 'headers' in request:
            # Remove authorization headers
            request['headers'].pop('Authorization', None)
            request['headers'].pop('Cookie', None)
    
    return event


def capture_exception(error, context=None):
    """
    Manually capture an exception with optional context
    
    Args:
        error: Exception to capture
        context: Optional dictionary of additional context
    """
    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_context(key, value)
        
        sentry_sdk.capture_exception(error)


def capture_message(message, level='info', context=None):
    """
    Capture a message (not an exception)
    
    Args:
        message: Message to capture
        level: Severity level (debug, info, warning, error, fatal)
        context: Optional dictionary of additional context
    """
    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_context(key, value)
        
        sentry_sdk.capture_message(message, level=level)


def set_user_context(user):
    """
    Set user context for error tracking
    
    Args:
        user: User object with id, email, and name
    """
    if user and hasattr(user, 'id'):
        sentry_sdk.set_user({
            "id": user.id,
            "email": user.email if hasattr(user, 'email') else None,
            "username": user.name if hasattr(user, 'name') else None,
            "role": user.role if hasattr(user, 'role') else None,
        })


def clear_user_context():
    """Clear user context (e.g., on logout)"""
    sentry_sdk.set_user(None)


def add_breadcrumb(message, category='default', level='info', data=None):
    """
    Add a breadcrumb for debugging context
    
    Args:
        message: Breadcrumb message
        category: Category (e.g., 'auth', 'query', 'navigation')
        level: Severity level
        data: Optional additional data
    """
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {}
    )


def start_transaction(name, op='http.server'):
    """
    Start a performance monitoring transaction
    
    Args:
        name: Transaction name
        op: Operation type
    
    Returns:
        Transaction object (use as context manager)
    """
    return sentry_sdk.start_transaction(name=name, op=op)


# Example usage in routes:
"""
from sentry_config import add_breadcrumb, set_user_context, start_transaction

@app.route('/api/example')
def example():
    # Add breadcrumb
    add_breadcrumb('User accessed example endpoint', category='api')
    
    # Start transaction for performance monitoring
    with start_transaction(name='api.example', op='http.server'):
        # Your code here
        pass
    
    return jsonify({'status': 'ok'})

@app.route('/login', methods=['POST'])
def login():
    # After successful login
    set_user_context(current_user)
    
    return redirect('/dashboard')
"""