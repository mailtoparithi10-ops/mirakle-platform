# decorators.py
from functools import wraps
from flask import abort
from flask_login import current_user


def role_required(*allowed_roles):
    """
    Decorator for restricting routes by user role.
    Example:
        @role_required("admin")
        @role_required("corporate", "admin")
        @role_required("founder", "connector")
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user or not current_user.is_authenticated:
                abort(401)  # Not logged in

            # Admin always allowed
            if current_user.role == "admin":
                return f(*args, **kwargs)

            # Check allowed roles
            if current_user.role not in allowed_roles:
                abort(403)  # Forbidden

            return f(*args, **kwargs)
        return wrapper
    return decorator
