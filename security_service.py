# security_service.py
"""
Security Service - Security hardening for enabler dashboard
Handles fraud detection, rate limiting, and security monitoring
"""

from datetime import datetime, timedelta
from extensions import db
from models import Referral, ReferralClick, RewardTransaction, User, EnablerLevel
from sqlalchemy import func
import hashlib
import re


class SecurityService:
    """Service class for security operations"""

    # ==========================================
    # FRAUD DETECTION
    # ==========================================

    @staticmethod
    def detect_suspicious_referral_patterns(enabler_id):
        """Detect suspicious referral patterns"""
        try:
            referrals = Referral.query.filter_by(enabler_id=enabler_id).all()
            
            flags = []
            risk_score = 0

            # Check 1: Too many referrals in short time
            recent_referrals = [r for r in referrals 
                              if r.created_at > datetime.utcnow() - timedelta(hours=24)]
            
            if len(recent_referrals) > 20:
                flags.append("High volume: 20+ referrals in 24 hours")
                risk_score += 30

            # Check 2: Same email domain pattern
            email_domains = {}
            for r in referrals:
                if r.startup_email:
                    domain = r.startup_email.split('@')[-1]
                    email_domains[domain] = email_domains.get(domain, 0) + 1

            for domain, count in email_domains.items():
                if count > 10:
                    flags.append(f"Suspicious: {count} referrals from {domain}")
                    risk_score += 20

            # Check 3: Similar startup names
            similar_names = SecurityService._find_similar_names(
                [r.startup_name for r in referrals]
            )
            if similar_names:
                flags.append(f"Similar names detected: {len(similar_names)} groups")
                risk_score += 15

            # Check 4: Referrals without clicks (link referrals)
            link_referrals = [r for r in referrals if r.is_link_referral]
            no_click_referrals = []
            for r in link_referrals:
                clicks = ReferralClick.query.filter_by(referral_id=r.id).count()
                if clicks == 0 and r.status == "successful":
                    no_click_referrals.append(r)

            if len(no_click_referrals) > 5:
                flags.append(f"Suspicious: {len(no_click_referrals)} successful referrals with no clicks")
                risk_score += 25

            # Check 5: Conversion rate too high
            successful = len([r for r in referrals if r.status == "successful"])
            if len(referrals) > 10:
                conversion_rate = successful / len(referrals)
                if conversion_rate > 0.8:
                    flags.append(f"Unusually high conversion: {conversion_rate*100:.1f}%")
                    risk_score += 20

            # Check 6: IP address patterns for clicks
            ip_patterns = SecurityService._analyze_ip_patterns(enabler_id)
            if ip_patterns["suspicious"]:
                flags.append(f"Suspicious IP patterns: {ip_patterns['message']}")
                risk_score += 25

            # Determine risk level
            if risk_score >= 70:
                risk_level = "high"
            elif risk_score >= 40:
                risk_level = "medium"
            elif risk_score >= 20:
                risk_level = "low"
            else:
                risk_level = "none"

            return {
                "success": True,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "flags": flags,
                "total_referrals": len(referrals),
                "successful_referrals": successful,
                "requires_review": risk_score >= 40
            }

        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def _find_similar_names(names):
        """Find groups of similar names"""
        similar_groups = []
        checked = set()

        for i, name1 in enumerate(names):
            if name1 in checked:
                continue

            group = [name1]
            for name2 in names[i+1:]:
                if name2 in checked:
                    continue

                # Simple similarity check
                similarity = SecurityService._string_similarity(name1.lower(), name2.lower())
                if similarity > 0.7:
                    group.append(name2)
                    checked.add(name2)

            if len(group) > 1:
                similar_groups.append(group)
                checked.add(name1)

        return similar_groups

    @staticmethod
    def _string_similarity(s1, s2):
        """Calculate string similarity (simple Jaccard similarity)"""
        set1 = set(s1.split())
        set2 = set(s2.split())
        
        if not set1 or not set2:
            return 0

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0

    @staticmethod
    def _analyze_ip_patterns(enabler_id):
        """Analyze IP address patterns for suspicious activity"""
        try:
            # Get all clicks for enabler's referrals
            referrals = Referral.query.filter_by(enabler_id=enabler_id).all()
            referral_ids = [r.id for r in referrals]

            clicks = ReferralClick.query.filter(
                ReferralClick.referral_id.in_(referral_ids)
            ).all()

            if not clicks:
                return {"suspicious": False, "message": "No clicks to analyze"}

            # Count clicks per IP
            ip_counts = {}
            for click in clicks:
                if click.ip_address:
                    ip_counts[click.ip_address] = ip_counts.get(click.ip_address, 0) + 1

            # Check for suspicious patterns
            max_clicks_per_ip = max(ip_counts.values()) if ip_counts else 0
            unique_ips = len(ip_counts)
            total_clicks = len(clicks)

            # Flag if one IP has too many clicks
            if max_clicks_per_ip > 20:
                return {
                    "suspicious": True,
                    "message": f"One IP has {max_clicks_per_ip} clicks"
                }

            # Flag if too few unique IPs for many clicks
            if total_clicks > 50 and unique_ips < 10:
                return {
                    "suspicious": True,
                    "message": f"Only {unique_ips} unique IPs for {total_clicks} clicks"
                }

            return {"suspicious": False, "message": "Normal IP patterns"}

        except Exception as e:
            return {"suspicious": False, "message": f"Error: {str(e)}"}

    # ==========================================
    # RATE LIMITING
    # ==========================================

    @staticmethod
    def check_rate_limit(enabler_id, action, limit, window_minutes=60):
        """Check if action exceeds rate limit"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)

            if action == "create_referral":
                count = Referral.query.filter(
                    Referral.enabler_id == enabler_id,
                    Referral.created_at >= cutoff_time
                ).count()

            elif action == "generate_link":
                count = Referral.query.filter(
                    Referral.enabler_id == enabler_id,
                    Referral.is_link_referral == True,
                    Referral.created_at >= cutoff_time
                ).count()

            elif action == "request_payout":
                count = RewardTransaction.query.filter(
                    RewardTransaction.enabler_id == enabler_id,
                    RewardTransaction.type == "payout",
                    RewardTransaction.created_at >= cutoff_time
                ).count()

            else:
                return {"allowed": True, "message": "Unknown action"}

            if count >= limit:
                return {
                    "allowed": False,
                    "message": f"Rate limit exceeded: {count}/{limit} in {window_minutes} minutes",
                    "retry_after": window_minutes
                }

            return {
                "allowed": True,
                "remaining": limit - count,
                "window_minutes": window_minutes
            }

        except Exception as e:
            return {"allowed": True, "message": f"Error: {str(e)}"}

    # ==========================================
    # INPUT VALIDATION
    # ==========================================

    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_bank_account(account_number, ifsc):
        """Validate bank account details"""
        errors = []

        # Validate account number (8-18 digits)
        if not account_number or not account_number.isdigit():
            errors.append("Account number must contain only digits")
        elif len(account_number) < 8 or len(account_number) > 18:
            errors.append("Account number must be 8-18 digits")

        # Validate IFSC (11 characters, format: XXXX0XXXXXX)
        ifsc_pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
        if not ifsc or not re.match(ifsc_pattern, ifsc.upper()):
            errors.append("Invalid IFSC code format")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    @staticmethod
    def sanitize_input(text, max_length=1000):
        """Sanitize user input"""
        if not text:
            return ""

        # Remove potentially dangerous characters
        text = re.sub(r'[<>]', '', text)
        
        # Limit length
        text = text[:max_length]
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        return text

    # ==========================================
    # AUDIT LOGGING
    # ==========================================

    @staticmethod
    def log_security_event(event_type, user_id, details, severity="info"):
        """Log security event"""
        try:
            from models import SecurityLog
            
            log = SecurityLog(
                event_type=event_type,
                user_id=user_id,
                details=details,
                severity=severity,
                ip_address=details.get("ip_address"),
                user_agent=details.get("user_agent")
            )

            db.session.add(log)
            db.session.commit()

            return {"success": True}

        except Exception as e:
            # Don't fail the main operation if logging fails
            print(f"Failed to log security event: {e}")
            return {"success": False, "message": str(e)}

    # ==========================================
    # ACCOUNT SECURITY
    # ==========================================

    @staticmethod
    def check_account_security(user_id):
        """Check account security status"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {"success": False, "message": "User not found"}

            issues = []
            recommendations = []

            # Check password strength (if not Google user)
            if user.password_hash:
                # Password exists, assume it's set
                pass
            else:
                if not user.google_id:
                    issues.append("No password set")
                    recommendations.append("Set a strong password")

            # Check email verification
            # (Assuming email_verified field exists or will be added)
            
            # Check bank details for enablers
            if user.role == "enabler":
                if not user.bank_account_number or not user.bank_ifsc:
                    recommendations.append("Add bank account details for payouts")

            # Check for suspicious activity
            if user.role == "enabler":
                fraud_check = SecurityService.detect_suspicious_referral_patterns(user_id)
                if fraud_check["success"] and fraud_check["risk_level"] in ["medium", "high"]:
                    issues.append(f"Suspicious activity detected: {fraud_check['risk_level']} risk")

            security_score = 100 - (len(issues) * 20)
            security_score = max(0, min(100, security_score))

            return {
                "success": True,
                "security_score": security_score,
                "issues": issues,
                "recommendations": recommendations,
                "status": "good" if security_score >= 80 else "needs_attention"
            }

        except Exception as e:
            return {"success": False, "message": str(e)}

    # ==========================================
    # PAYOUT VERIFICATION
    # ==========================================

    @staticmethod
    def verify_payout_eligibility(enabler_id, amount):
        """Verify if enabler is eligible for payout"""
        try:
            user = User.query.get(enabler_id)
            if not user:
                return {"eligible": False, "reason": "User not found"}

            if user.role != "enabler":
                return {"eligible": False, "reason": "Not an enabler account"}

            # Check bank details
            if not user.bank_account_number or not user.bank_ifsc:
                return {"eligible": False, "reason": "Bank details not configured"}

            # Check minimum amount
            if amount < 1000:
                return {"eligible": False, "reason": "Minimum payout amount is ₹1,000"}

            # Check for fraud flags
            fraud_check = SecurityService.detect_suspicious_referral_patterns(enabler_id)
            if fraud_check["success"] and fraud_check["risk_level"] == "high":
                return {
                    "eligible": False,
                    "reason": "Account flagged for review",
                    "requires_manual_review": True
                }

            # Check account age (must be at least 7 days old)
            account_age = (datetime.utcnow() - user.created_at).days
            if account_age < 7:
                return {
                    "eligible": False,
                    "reason": f"Account must be at least 7 days old (current: {account_age} days)"
                }

            # Check for pending payouts
            pending_payouts = RewardTransaction.query.filter_by(
                enabler_id=enabler_id,
                type="payout",
                status="pending"
            ).count()

            if pending_payouts > 0:
                return {
                    "eligible": False,
                    "reason": "You have pending payout requests"
                }

            return {"eligible": True, "reason": "Eligible for payout"}

        except Exception as e:
            return {"eligible": False, "reason": str(e)}

    # ==========================================
    # DATA ENCRYPTION
    # ==========================================

    @staticmethod
    def hash_sensitive_data(data):
        """Hash sensitive data for storage"""
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    def mask_bank_account(account_number):
        """Mask bank account number for display"""
        if not account_number or len(account_number) < 4:
            return "****"
        
        return "X" * (len(account_number) - 4) + account_number[-4:]

    @staticmethod
    def mask_email(email):
        """Mask email for display"""
        if not email or '@' not in email:
            return "***@***.com"
        
        parts = email.split('@')
        username = parts[0]
        domain = parts[1]
        
        if len(username) <= 2:
            masked_username = username[0] + "*"
        else:
            masked_username = username[0] + "*" * (len(username) - 2) + username[-1]
        
        return f"{masked_username}@{domain}"
