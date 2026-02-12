# routes/messaging.py
"""
Messaging routes for enabler dashboard
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from message_service import MessageService

bp = Blueprint("messaging", __name__, url_prefix="/api/messages")


@bp.route("/inbox", methods=["GET"])
@login_required
def get_inbox():
    """Get inbox messages"""
    message_type = request.args.get("type")
    unread_only = request.args.get("unread_only", "false").lower() == "true"
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))

    result = MessageService.get_inbox(
        current_user.id,
        message_type,
        unread_only,
        page,
        per_page
    )

    return jsonify(result)


@bp.route("/sent", methods=["GET"])
@login_required
def get_sent():
    """Get sent messages"""
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))

    result = MessageService.get_sent_messages(current_user.id, page, per_page)
    return jsonify(result)


@bp.route("/conversation/<int:other_user_id>", methods=["GET"])
@login_required
def get_conversation(other_user_id):
    """Get conversation with another user"""
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))

    result = MessageService.get_conversation(
        current_user.id,
        other_user_id,
        page,
        per_page
    )

    return jsonify(result)


@bp.route("/send", methods=["POST"])
@login_required
def send_message():
    """Send a message"""
    data = request.get_json()

    required_fields = ["recipient_id", "subject", "body"]
    if not all(field in data for field in required_fields):
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    # Rate limiting
    from security_service import SecurityService
    rate_check = SecurityService.check_rate_limit(
        current_user.id,
        "send_message",
        limit=50,
        window_minutes=60
    )

    if not rate_check["allowed"]:
        return jsonify({
            "success": False,
            "message": rate_check["message"]
        }), 429

    # Sanitize input
    subject = SecurityService.sanitize_input(data["subject"], max_length=300)
    body = SecurityService.sanitize_input(data["body"], max_length=5000)

    result = MessageService.send_message(
        sender_id=current_user.id,
        recipient_id=data["recipient_id"],
        subject=subject,
        body=body,
        message_type=data.get("message_type", "direct"),
        referral_id=data.get("referral_id"),
        opportunity_id=data.get("opportunity_id")
    )

    return jsonify(result)


@bp.route("/<int:message_id>/read", methods=["POST"])
@login_required
def mark_as_read(message_id):
    """Mark a message as read"""
    result = MessageService.mark_as_read(message_id, current_user.id)
    return jsonify(result)


@bp.route("/mark-all-read", methods=["POST"])
@login_required
def mark_all_as_read():
    """Mark all messages as read"""
    result = MessageService.mark_all_as_read(current_user.id)
    return jsonify(result)


@bp.route("/<int:message_id>", methods=["DELETE"])
@login_required
def delete_message(message_id):
    """Delete a message"""
    result = MessageService.delete_message(message_id, current_user.id)
    return jsonify(result)


@bp.route("/unread-count", methods=["GET"])
@login_required
def unread_count():
    """Get unread message count"""
    result = MessageService.get_unread_count(current_user.id)
    return jsonify(result)


@bp.route("/templates", methods=["GET"])
@login_required
def get_templates():
    """Get message templates"""
    templates = MessageService.get_message_templates(current_user.role)
    return jsonify({"success": True, "templates": templates})
