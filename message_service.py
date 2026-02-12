# message_service.py
"""
Message Service - Real-time messaging system for enabler dashboard
Handles conversations, notifications, and message management
"""

from datetime import datetime
from extensions import db
from models import User, Referral, Opportunity, Startup
from sqlalchemy import or_, and_


class MessageService:
    """Service class for messaging operations"""

    # ==========================================
    # MESSAGE MANAGEMENT
    # ==========================================

    @staticmethod
    def send_message(sender_id, recipient_id, subject, body, message_type="direct", 
                     referral_id=None, opportunity_id=None):
        """Send a message"""
        try:
            from models import Message
            
            message = Message(
                sender_id=sender_id,
                recipient_id=recipient_id,
                subject=subject,
                body=body,
                message_type=message_type,
                referral_id=referral_id,
                opportunity_id=opportunity_id,
                is_read=False
            )

            db.session.add(message)
            db.session.commit()

            # Send notification
            MessageService._send_message_notification(message)

            return {
                "success": True,
                "message": message.to_dict(),
                "message_text": "Message sent successfully"
            }

        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_inbox(user_id, message_type=None, unread_only=False, page=1, per_page=20):
        """Get inbox messages for a user"""
        try:
            from models import Message
            
            query = Message.query.filter_by(recipient_id=user_id)

            if message_type:
                query = query.filter_by(message_type=message_type)

            if unread_only:
                query = query.filter_by(is_read=False)

            query = query.order_by(Message.created_at.desc())
            total = query.count()
            messages = query.offset((page - 1) * per_page).limit(per_page).all()

            # Enrich messages with sender info
            result = []
            for msg in messages:
                msg_dict = msg.to_dict()
                sender = User.query.get(msg.sender_id)
                if sender:
                    msg_dict["sender_name"] = sender.name
                    msg_dict["sender_email"] = sender.email
                    msg_dict["sender_role"] = sender.role
                    msg_dict["sender_avatar"] = sender.profile_pic

                # Add referral/opportunity context
                if msg.referral_id:
                    referral = Referral.query.get(msg.referral_id)
                    if referral:
                        msg_dict["referral_startup"] = referral.startup_name
                        opp = Opportunity.query.get(referral.opportunity_id)
                        if opp:
                            msg_dict["referral_program"] = opp.title

                if msg.opportunity_id:
                    opp = Opportunity.query.get(msg.opportunity_id)
                    if opp:
                        msg_dict["opportunity_title"] = opp.title

                result.append(msg_dict)

            return {
                "success": True,
                "messages": result,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": (total + per_page - 1) // per_page
                },
                "unread_count": Message.query.filter_by(
                    recipient_id=user_id,
                    is_read=False
                ).count()
            }

        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_sent_messages(user_id, page=1, per_page=20):
        """Get sent messages for a user"""
        try:
            from models import Message
            
            query = Message.query.filter_by(sender_id=user_id)
            query = query.order_by(Message.created_at.desc())
            total = query.count()
            messages = query.offset((page - 1) * per_page).limit(per_page).all()

            result = []
            for msg in messages:
                msg_dict = msg.to_dict()
                recipient = User.query.get(msg.recipient_id)
                if recipient:
                    msg_dict["recipient_name"] = recipient.name
                    msg_dict["recipient_email"] = recipient.email
                    msg_dict["recipient_role"] = recipient.role
                result.append(msg_dict)

            return {
                "success": True,
                "messages": result,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": (total + per_page - 1) // per_page
                }
            }

        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_conversation(user_id, other_user_id, page=1, per_page=50):
        """Get conversation between two users"""
        try:
            from models import Message
            
            query = Message.query.filter(
                or_(
                    and_(Message.sender_id == user_id, Message.recipient_id == other_user_id),
                    and_(Message.sender_id == other_user_id, Message.recipient_id == user_id)
                )
            )

            query = query.order_by(Message.created_at.asc())
            total = query.count()
            messages = query.offset((page - 1) * per_page).limit(per_page).all()

            # Mark messages as read
            for msg in messages:
                if msg.recipient_id == user_id and not msg.is_read:
                    msg.is_read = True
                    msg.read_at = datetime.utcnow()

            db.session.commit()

            return {
                "success": True,
                "messages": [msg.to_dict() for msg in messages],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": (total + per_page - 1) // per_page
                }
            }

        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    @staticmethod
    def mark_as_read(message_id, user_id):
        """Mark a message as read"""
        try:
            from models import Message
            
            message = Message.query.get(message_id)
            if not message:
                return {"success": False, "message": "Message not found"}

            if message.recipient_id != user_id:
                return {"success": False, "message": "Unauthorized"}

            message.is_read = True
            message.read_at = datetime.utcnow()
            db.session.commit()

            return {"success": True, "message": "Message marked as read"}

        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    @staticmethod
    def mark_all_as_read(user_id):
        """Mark all messages as read for a user"""
        try:
            from models import Message
            
            messages = Message.query.filter_by(
                recipient_id=user_id,
                is_read=False
            ).all()

            for msg in messages:
                msg.is_read = True
                msg.read_at = datetime.utcnow()

            db.session.commit()

            return {
                "success": True,
                "count": len(messages),
                "message": f"Marked {len(messages)} messages as read"
            }

        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    @staticmethod
    def delete_message(message_id, user_id):
        """Delete a message"""
        try:
            from models import Message
            
            message = Message.query.get(message_id)
            if not message:
                return {"success": False, "message": "Message not found"}

            # Only recipient can delete
            if message.recipient_id != user_id:
                return {"success": False, "message": "Unauthorized"}

            db.session.delete(message)
            db.session.commit()

            return {"success": True, "message": "Message deleted"}

        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}

    # ==========================================
    # AUTOMATED MESSAGES
    # ==========================================

    @staticmethod
    def send_referral_notification(referral_id):
        """Send notification about new referral"""
        try:
            referral = Referral.query.get(referral_id)
            if not referral:
                return {"success": False, "message": "Referral not found"}

            opportunity = Opportunity.query.get(referral.opportunity_id)
            if not opportunity:
                return {"success": False, "message": "Opportunity not found"}

            # Send to enabler
            subject = f"Referral Submitted: {referral.startup_name}"
            body = f"""Your referral for {referral.startup_name} to {opportunity.title} has been submitted successfully.

We'll notify you once the startup applies and when there are updates on their application status.

Referral Details:
- Startup: {referral.startup_name}
- Program: {opportunity.title}
- Status: {referral.status}
- Date: {referral.created_at.strftime('%B %d, %Y')}

Track your referral in the My Referrals section of your dashboard.
"""

            MessageService.send_message(
                sender_id=1,  # System user
                recipient_id=referral.enabler_id,
                subject=subject,
                body=body,
                message_type="system",
                referral_id=referral_id,
                opportunity_id=referral.opportunity_id
            )

            return {"success": True}

        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def send_reward_notification(transaction_id):
        """Send notification about reward"""
        try:
            from models import RewardTransaction
            
            transaction = RewardTransaction.query.get(transaction_id)
            if not transaction:
                return {"success": False, "message": "Transaction not found"}

            subject = f"Reward Earned: ₹{abs(transaction.amount_money):,.2f}"
            body = f"""Congratulations! You've earned a reward.

Reward Details:
- Amount: ₹{abs(transaction.amount_money):,.2f}
- Type: {transaction.type.title()}
- Program: {transaction.program_name or 'N/A'}
- Startup: {transaction.startup_name or 'N/A'}
- Status: {transaction.status.title()}
- Date: {transaction.created_at.strftime('%B %d, %Y')}

{transaction.description or ''}

View your rewards in the Rewards & Earnings section of your dashboard.
"""

            MessageService.send_message(
                sender_id=1,  # System user
                recipient_id=transaction.enabler_id,
                subject=subject,
                body=body,
                message_type="reward"
            )

            return {"success": True}

        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def send_payout_notification(transaction_id):
        """Send notification about payout"""
        try:
            from models import RewardTransaction
            
            transaction = RewardTransaction.query.get(transaction_id)
            if not transaction:
                return {"success": False, "message": "Transaction not found"}

            if transaction.status == "paid":
                subject = "Payout Completed"
                body = f"""Your payout has been processed successfully!

Payout Details:
- Amount: ₹{abs(transaction.amount_money):,.2f}
- Method: {transaction.payout_method or 'Bank Transfer'}
- Reference: {transaction.payout_reference or 'N/A'}
- Date: {transaction.paid_at.strftime('%B %d, %Y') if transaction.paid_at else 'N/A'}

The amount should reflect in your account within 1-3 business days.

Thank you for being a valued enabler!
"""
            else:
                subject = "Payout Request Received"
                body = f"""We've received your payout request.

Payout Details:
- Amount: ₹{abs(transaction.amount_money):,.2f}
- Method: {transaction.payout_method or 'Bank Transfer'}
- Status: {transaction.status.title()}
- Date: {transaction.created_at.strftime('%B %d, %Y')}

Your request is being processed and will be completed within 3-5 business days.

We'll notify you once the payout is completed.
"""

            MessageService.send_message(
                sender_id=1,  # System user
                recipient_id=transaction.enabler_id,
                subject=subject,
                body=body,
                message_type="system"
            )

            return {"success": True}

        except Exception as e:
            return {"success": False, "message": str(e)}

    # ==========================================
    # MESSAGE TEMPLATES
    # ==========================================

    @staticmethod
    def get_message_templates(user_role):
        """Get message templates for a user role"""
        templates = {
            "enabler": [
                {
                    "id": "intro_startup",
                    "name": "Introduction to Startup",
                    "subject": "Introduction - {enabler_name}",
                    "body": """Hi {startup_name},

I'm {enabler_name}, and I work with startups in the {sector} space. I came across your company and was impressed by {specific_detail}.

I'd like to introduce you to {program_name}, which I think could be a great fit for your company because {reason}.

Would you be interested in learning more? I'd be happy to provide more details and help with the application process.

Best regards,
{enabler_name}"""
                },
                {
                    "id": "follow_up",
                    "name": "Follow Up on Referral",
                    "subject": "Following up on {program_name}",
                    "body": """Hi {startup_name},

I wanted to follow up on the {program_name} opportunity I shared with you.

The application deadline is {deadline}, and I wanted to make sure you have everything you need to apply.

Let me know if you have any questions or need any assistance!

Best regards,
{enabler_name}"""
                },
                {
                    "id": "congratulations",
                    "name": "Congratulations on Selection",
                    "subject": "Congratulations! 🎉",
                    "body": """Hi {startup_name},

Congratulations on being selected for {program_name}! This is a fantastic achievement.

I'm thrilled to have been able to connect you with this opportunity. Wishing you all the best as you embark on this journey!

Feel free to reach out if you need anything in the future.

Best regards,
{enabler_name}"""
                }
            ],
            "startup": [
                {
                    "id": "thank_you",
                    "name": "Thank You for Referral",
                    "subject": "Thank you for the referral",
                    "body": """Hi {enabler_name},

Thank you so much for referring us to {program_name}. We really appreciate you thinking of us for this opportunity.

We've reviewed the program details and {action_taken}.

Thanks again for your support!

Best regards,
{startup_name}"""
                }
            ]
        }

        return templates.get(user_role, [])

    # ==========================================
    # NOTIFICATIONS
    # ==========================================

    @staticmethod
    def _send_message_notification(message):
        """Send notification about new message"""
        try:
            from email_service import EmailService
            
            recipient = User.query.get(message.recipient_id)
            sender = User.query.get(message.sender_id)

            if not recipient or not sender:
                return

            # Send email notification
            EmailService.send_message_notification(
                recipient.email,
                recipient.name,
                sender.name,
                message.subject,
                message.body[:200]  # Preview
            )

        except Exception as e:
            print(f"Failed to send message notification: {e}")

    @staticmethod
    def get_unread_count(user_id):
        """Get unread message count"""
        try:
            from models import Message
            
            count = Message.query.filter_by(
                recipient_id=user_id,
                is_read=False
            ).count()

            return {"success": True, "count": count}

        except Exception as e:
            return {"success": False, "message": str(e)}
