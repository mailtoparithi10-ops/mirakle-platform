# routes/payments.py
"""
Payment routes for enabler payouts
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from payment_service import PaymentService
from security_service import SecurityService

bp = Blueprint("payments", __name__, url_prefix="/api/payments")
payment_service = PaymentService()


@bp.route("/payout/request", methods=["POST"])
@login_required
def request_payout():
    """Request a payout"""
    if current_user.role not in ("enabler", "admin"):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    data = request.get_json()
    
    if "amount" not in data:
        return jsonify({"success": False, "message": "amount required"}), 400

    amount = float(data["amount"])
    payout_method = data.get("payout_method", "IMPS")

    # Verify eligibility
    eligibility = SecurityService.verify_payout_eligibility(current_user.id, amount)
    if not eligibility["eligible"]:
        return jsonify({
            "success": False,
            "message": eligibility["reason"],
            "requires_manual_review": eligibility.get("requires_manual_review", False)
        }), 400

    # Create payout request (will be approved by admin)
    from enabler_service import EnablerService
    result = EnablerService.request_payout(
        current_user.id,
        amount,
        payout_method
    )

    return jsonify(result)


@bp.route("/bank-account/add", methods=["POST"])
@login_required
def add_bank_account():
    """Add or update bank account details"""
    if current_user.role not in ("enabler", "admin"):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    data = request.get_json()
    
    required_fields = ["account_name", "account_number", "ifsc", "bank_name"]
    if not all(field in data for field in required_fields):
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    # Validate bank details
    validation = SecurityService.validate_bank_account(
        data["account_number"],
        data["ifsc"]
    )

    if not validation["valid"]:
        return jsonify({
            "success": False,
            "message": "Invalid bank details",
            "errors": validation["errors"]
        }), 400

    # Update user bank details
    from models import User
    from extensions import db
    
    user = User.query.get(current_user.id)
    user.bank_account_name = data["account_name"]
    user.bank_account_number = data["account_number"]
    user.bank_ifsc = data["ifsc"].upper()
    user.bank_name = data["bank_name"]

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Bank account details saved successfully"
    })


@bp.route("/bank-account/verify", methods=["POST"])
@login_required
def verify_bank_account():
    """Verify bank account details"""
    if current_user.role not in ("enabler", "admin"):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    data = request.get_json()
    
    if "account_number" not in data or "ifsc" not in data:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    result = payment_service.verify_bank_account(
        data["account_number"],
        data["ifsc"]
    )

    return jsonify(result)


@bp.route("/payout/history", methods=["GET"])
@login_required
def payout_history():
    """Get payout history"""
    if current_user.role not in ("enabler", "admin"):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    result = payment_service.get_payout_report(current_user.id)
    return jsonify(result)


@bp.route("/payout/status/<payout_id>", methods=["GET"])
@login_required
def payout_status(payout_id):
    """Get payout status"""
    if current_user.role not in ("enabler", "admin"):
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    result = payment_service.get_payout_status(payout_id)
    return jsonify(result)


# Admin routes
@bp.route("/admin/payouts/pending", methods=["GET"])
@login_required
def admin_pending_payouts():
    """Get all pending payouts (admin only)"""
    if current_user.role != "admin":
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    result = payment_service.get_pending_payouts()
    return jsonify(result)


@bp.route("/admin/payout/<int:transaction_id>/approve", methods=["POST"])
@login_required
def admin_approve_payout(transaction_id):
    """Approve a payout request (admin only)"""
    if current_user.role != "admin":
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    result = payment_service.approve_payout(transaction_id, current_user.id)
    return jsonify(result)


@bp.route("/admin/payout/<int:transaction_id>/reject", methods=["POST"])
@login_required
def admin_reject_payout(transaction_id):
    """Reject a payout request (admin only)"""
    if current_user.role != "admin":
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    data = request.get_json()
    reason = data.get("reason", "No reason provided")

    result = payment_service.reject_payout(transaction_id, current_user.id, reason)
    return jsonify(result)


# Webhook endpoint
@bp.route("/webhook/razorpay", methods=["POST"])
def razorpay_webhook():
    """Handle Razorpay webhooks"""
    try:
        payload = request.get_data(as_text=True)
        signature = request.headers.get("X-Razorpay-Signature")

        from config import Config
        
        # Verify signature
        if not payment_service.verify_webhook_signature(
            payload,
            signature,
            Config.RAZORPAY_WEBHOOK_SECRET
        ):
            return jsonify({"success": False, "message": "Invalid signature"}), 400

        # Process webhook
        event_data = request.get_json()
        result = payment_service.handle_payout_webhook(event_data)

        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
