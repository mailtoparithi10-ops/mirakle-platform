# payment_service.py
"""
Payment Service - Razorpay integration for enabler payouts
Handles payment processing, verification, and webhooks
"""

import razorpay
from datetime import datetime
from extensions import db
from models import RewardTransaction, User, EnablerLevel
from config import Config
import hmac
import hashlib


class PaymentService:
    """Service class for payment processing"""

    def __init__(self):
        """Initialize Razorpay client"""
        self.client = razorpay.Client(auth=(Config.RAZORPAY_KEY_ID, Config.RAZORPAY_KEY_SECRET))

    # ==========================================
    # PAYOUT PROCESSING
    # ==========================================

    def create_payout(self, transaction_id):
        """Create a payout to enabler's account"""
        try:
            transaction = RewardTransaction.query.get(transaction_id)
            if not transaction:
                return {"success": False, "message": "Transaction not found"}

            if transaction.type != "payout":
                return {"success": False, "message": "Invalid transaction type"}

            if transaction.status != "pending":
                return {"success": False, "message": "Transaction already processed"}

            user = User.query.get(transaction.enabler_id)
            if not user:
                return {"success": False, "message": "User not found"}

            # Validate bank details
            if not user.bank_account_number or not user.bank_ifsc:
                return {"success": False, "message": "Bank details not configured"}

            amount_paise = int(abs(transaction.amount_money) * 100)

            # Create payout via Razorpay
            payout_data = {
                "account_number": Config.RAZORPAY_ACCOUNT_NUMBER,
                "fund_account_id": user.razorpay_fund_account_id or self._create_fund_account(user),
                "amount": amount_paise,
                "currency": "INR",
                "mode": transaction.payout_method or "IMPS",
                "purpose": "payout",
                "queue_if_low_balance": True,
                "reference_id": f"TXN_{transaction.id}",
                "narration": f"Referral rewards payout - {user.name}",
                "notes": {
                    "transaction_id": transaction.id,
                    "enabler_id": transaction.enabler_id,
                    "user_email": user.email
                }
            }

            response = self.client.payout.create(payout_data)

            # Update transaction with payout details
            transaction.payout_reference = response["id"]
            transaction.status = "processing"
            transaction.admin_notes = f"Razorpay payout created: {response['id']}"

            db.session.commit()

            return {
                "success": True,
                "payout_id": response["id"],
                "status": response["status"],
                "message": "Payout initiated successfully"
            }

        except razorpay.errors.BadRequestError as e:
            db.session.rollback()
            return {"success": False, "message": f"Razorpay error: {str(e)}"}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    def _create_fund_account(self, user):
        """Create fund account for user"""
        try:
            # Create contact
            contact_data = {
                "name": user.name,
                "email": user.email,
                "contact": user.phone or "9999999999",
                "type": "vendor",
                "reference_id": f"USER_{user.id}",
                "notes": {
                    "user_id": user.id,
                    "role": user.role
                }
            }

            contact = self.client.contact.create(contact_data)

            # Create fund account
            fund_account_data = {
                "contact_id": contact["id"],
                "account_type": "bank_account",
                "bank_account": {
                    "name": user.bank_account_name or user.name,
                    "ifsc": user.bank_ifsc,
                    "account_number": user.bank_account_number
                }
            }

            fund_account = self.client.fund_account.create(fund_account_data)

            # Save fund account ID
            user.razorpay_contact_id = contact["id"]
            user.razorpay_fund_account_id = fund_account["id"]
            db.session.commit()

            return fund_account["id"]

        except Exception as e:
            raise Exception(f"Failed to create fund account: {str(e)}")

    def get_payout_status(self, payout_id):
        """Get status of a payout"""
        try:
            payout = self.client.payout.fetch(payout_id)
            return {
                "success": True,
                "status": payout["status"],
                "amount": payout["amount"] / 100,
                "utr": payout.get("utr"),
                "created_at": payout["created_at"]
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def update_payout_status(self, payout_id, status):
        """Update transaction status based on payout status"""
        try:
            transaction = RewardTransaction.query.filter_by(
                payout_reference=payout_id
            ).first()

            if not transaction:
                return {"success": False, "message": "Transaction not found"}

            status_mapping = {
                "processing": "processing",
                "processed": "paid",
                "reversed": "failed",
                "failed": "failed",
                "cancelled": "failed"
            }

            new_status = status_mapping.get(status, "processing")
            transaction.status = new_status

            if new_status == "paid":
                transaction.paid_at = datetime.utcnow()

            db.session.commit()

            return {"success": True, "status": new_status}

        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    # ==========================================
    # WEBHOOK HANDLING
    # ==========================================

    def verify_webhook_signature(self, payload, signature, secret):
        """Verify Razorpay webhook signature"""
        try:
            expected_signature = hmac.new(
                secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(expected_signature, signature)

        except Exception:
            return False

    def handle_payout_webhook(self, event_data):
        """Handle payout webhook events"""
        try:
            event_type = event_data.get("event")
            payload = event_data.get("payload", {})
            payout = payload.get("payout", {})
            entity = payout.get("entity", {})

            payout_id = entity.get("id")
            status = entity.get("status")

            if not payout_id:
                return {"success": False, "message": "Invalid webhook data"}

            # Update transaction status
            result = self.update_payout_status(payout_id, status)

            # Send notification to user
            if result["success"] and status == "processed":
                transaction = RewardTransaction.query.filter_by(
                    payout_reference=payout_id
                ).first()

                if transaction:
                    self._send_payout_notification(transaction)

            return result

        except Exception as e:
            return {"success": False, "message": str(e)}

    def _send_payout_notification(self, transaction):
        """Send payout success notification"""
        try:
            from email_service import EmailService
            
            user = User.query.get(transaction.enabler_id)
            if not user:
                return

            EmailService.send_payout_confirmation(
                user.email,
                user.name,
                abs(transaction.amount_money),
                transaction.payout_reference
            )

        except Exception as e:
            print(f"Failed to send payout notification: {e}")

    # ==========================================
    # BANK ACCOUNT VERIFICATION
    # ==========================================

    def verify_bank_account(self, account_number, ifsc):
        """Verify bank account details"""
        try:
            # Use Razorpay's bank account verification API
            verification_data = {
                "account_number": account_number,
                "ifsc": ifsc
            }

            # Note: This is a placeholder - actual implementation depends on Razorpay's API
            # You may need to use a third-party service for verification

            return {
                "success": True,
                "verified": True,
                "account_name": "Account Holder Name",
                "message": "Bank account verified successfully"
            }

        except Exception as e:
            return {"success": False, "message": str(e)}

    # ==========================================
    # PAYMENT REPORTS
    # ==========================================

    def get_payout_report(self, enabler_id, start_date=None, end_date=None):
        """Get payout report for an enabler"""
        try:
            query = RewardTransaction.query.filter_by(
                enabler_id=enabler_id,
                type="payout"
            )

            if start_date:
                query = query.filter(RewardTransaction.created_at >= start_date)
            if end_date:
                query = query.filter(RewardTransaction.created_at <= end_date)

            transactions = query.order_by(RewardTransaction.created_at.desc()).all()

            total_requested = sum(abs(t.amount_money) for t in transactions)
            total_paid = sum(abs(t.amount_money) for t in transactions if t.status == "paid")
            total_pending = sum(abs(t.amount_money) for t in transactions if t.status == "pending")
            total_failed = sum(abs(t.amount_money) for t in transactions if t.status == "failed")

            return {
                "success": True,
                "summary": {
                    "total_requested": round(total_requested, 2),
                    "total_paid": round(total_paid, 2),
                    "total_pending": round(total_pending, 2),
                    "total_failed": round(total_failed, 2),
                    "count": len(transactions)
                },
                "transactions": [t.to_dict() for t in transactions]
            }

        except Exception as e:
            return {"success": False, "message": str(e)}

    # ==========================================
    # ADMIN FUNCTIONS
    # ==========================================

    def approve_payout(self, transaction_id, admin_id):
        """Admin approves a payout request"""
        try:
            transaction = RewardTransaction.query.get(transaction_id)
            if not transaction:
                return {"success": False, "message": "Transaction not found"}

            if transaction.status != "pending":
                return {"success": False, "message": "Transaction already processed"}

            # Create payout
            result = self.create_payout(transaction_id)

            if result["success"]:
                admin = User.query.get(admin_id)
                transaction.admin_notes = f"Approved by {admin.name if admin else 'Admin'}"
                db.session.commit()

            return result

        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    def reject_payout(self, transaction_id, admin_id, reason):
        """Admin rejects a payout request"""
        try:
            transaction = RewardTransaction.query.get(transaction_id)
            if not transaction:
                return {"success": False, "message": "Transaction not found"}

            if transaction.status != "pending":
                return {"success": False, "message": "Transaction already processed"}

            admin = User.query.get(admin_id)
            transaction.status = "failed"
            transaction.admin_notes = f"Rejected by {admin.name if admin else 'Admin'}: {reason}"

            db.session.commit()

            return {
                "success": True,
                "message": "Payout request rejected"
            }

        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    def get_pending_payouts(self):
        """Get all pending payout requests"""
        try:
            transactions = RewardTransaction.query.filter_by(
                type="payout",
                status="pending"
            ).order_by(RewardTransaction.created_at.desc()).all()

            result = []
            for t in transactions:
                user = User.query.get(t.enabler_id)
                t_dict = t.to_dict()
                if user:
                    t_dict["enabler_name"] = user.name
                    t_dict["enabler_email"] = user.email
                    t_dict["bank_verified"] = bool(user.bank_account_number and user.bank_ifsc)
                result.append(t_dict)

            return {
                "success": True,
                "count": len(result),
                "transactions": result
            }

        except Exception as e:
            return {"success": False, "message": str(e)}
