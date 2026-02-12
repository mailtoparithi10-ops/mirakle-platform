"""
Email Service for InnoBridge Platform
Handles all email notifications and communications
"""

from flask import current_app, render_template_string, url_for
from flask_mail import Message
from extensions import mail
from threading import Thread
import os


def send_async_email(app, msg):
    """Send email asynchronously in background thread"""
    with app.app_context():
        try:
            mail.send(msg)
            print(f"✅ Email sent successfully to {msg.recipients}")
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            # Log to Sentry if available
            try:
                from sentry_config import capture_exception
                capture_exception(e, context={'email': msg.subject})
            except:
                pass


def send_email(subject, recipients, text_body, html_body, sender=None):
    """
    Send email with both text and HTML versions
    
    Args:
        subject: Email subject
        recipients: List of recipient email addresses
        text_body: Plain text version
        html_body: HTML version
        sender: Sender email (optional, uses default)
    """
    # Check if email is configured
    if not current_app.config.get('MAIL_USERNAME'):
        print("⚠️  Email not configured. Skipping email send.")
        print(f"   Subject: {subject}")
        print(f"   Recipients: {recipients}")
        return False
    
    # Check if email sending is suppressed (for testing)
    if current_app.config.get('MAIL_SUPPRESS_SEND'):
        print(f"📧 Email suppressed (testing mode): {subject} to {recipients}")
        return True
    
    try:
        msg = Message(
            subject=subject,
            recipients=recipients if isinstance(recipients, list) else [recipients],
            body=text_body,
            html=html_body,
            sender=sender or current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # Send asynchronously
        Thread(
            target=send_async_email,
            args=(current_app._get_current_object(), msg)
        ).start()
        
        return True
    except Exception as e:
        print(f"❌ Error preparing email: {e}")
        return False


# -----------------------------------------
# REGISTRATION EMAILS
# -----------------------------------------

def send_welcome_email(user):
    """Send welcome email after successful registration"""
    subject = "Welcome to InnoBridge! 🚀"
    
    # Determine dashboard URL based on role
    dashboard_urls = {
        'startup': '/startup',
        'founder': '/startup',
        'corporate': '/corporate',
        'enabler': '/enabler',
        'admin': '/admin'
    }
    dashboard_url = dashboard_urls.get(user.role, '/')
    
    text_body = f"""
Hi {user.name},

Welcome to InnoBridge! We're excited to have you join our innovation ecosystem.

Your account has been successfully created with the following details:
- Email: {user.email}
- Role: {user.role.capitalize()}
- Company: {user.company or 'Not specified'}

Get started by logging in to your dashboard:
{url_for('index', _external=True)}{dashboard_url}

What you can do next:
- Complete your profile
- Explore opportunities
- Connect with other members
- Join meetings and events

If you have any questions, feel free to reach out to our support team.

Best regards,
The InnoBridge Team

---
This is an automated message. Please do not reply to this email.
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .info-box {{ background: white; padding: 15px; border-left: 4px solid #667eea; margin: 20px 0; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Welcome to InnoBridge!</h1>
        </div>
        <div class="content">
            <p>Hi <strong>{user.name}</strong>,</p>
            
            <p>Welcome to InnoBridge! We're excited to have you join our innovation ecosystem.</p>
            
            <div class="info-box">
                <strong>Your Account Details:</strong><br>
                📧 Email: {user.email}<br>
                👤 Role: {user.role.capitalize()}<br>
                🏢 Company: {user.company or 'Not specified'}
            </div>
            
            <p>Get started by accessing your dashboard:</p>
            
            <center>
                <a href="{url_for('index', _external=True)}{dashboard_url}" class="button">Go to Dashboard</a>
            </center>
            
            <p><strong>What you can do next:</strong></p>
            <ul>
                <li>Complete your profile</li>
                <li>Explore opportunities</li>
                <li>Connect with other members</li>
                <li>Join meetings and events</li>
            </ul>
            
            <p>If you have any questions, feel free to reach out to our support team.</p>
            
            <p>Best regards,<br><strong>The InnoBridge Team</strong></p>
        </div>
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
"""
    
    return send_email(subject, user.email, text_body, html_body)


# -----------------------------------------
# PASSWORD RESET EMAILS
# -----------------------------------------

def send_password_reset_email(user, reset_token):
    """Send password reset email with token"""
    subject = "Reset Your InnoBridge Password"
    
    reset_url = url_for('auth.reset_password', token=reset_token, _external=True)
    
    text_body = f"""
Hi {user.name},

You requested to reset your password for your InnoBridge account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour for security reasons.

If you didn't request this password reset, please ignore this email. Your password will remain unchanged.

Best regards,
The InnoBridge Team

---
This is an automated message. Please do not reply to this email.
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #667eea; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 Password Reset Request</h1>
        </div>
        <div class="content">
            <p>Hi <strong>{user.name}</strong>,</p>
            
            <p>You requested to reset your password for your InnoBridge account.</p>
            
            <center>
                <a href="{reset_url}" class="button">Reset Password</a>
            </center>
            
            <div class="warning">
                ⚠️ <strong>Security Notice:</strong><br>
                This link will expire in 1 hour for security reasons.
            </div>
            
            <p>If you didn't request this password reset, please ignore this email. Your password will remain unchanged.</p>
            
            <p>Best regards,<br><strong>The InnoBridge Team</strong></p>
        </div>
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
"""
    
    return send_email(subject, user.email, text_body, html_body)


# -----------------------------------------
# MEETING EMAILS
# -----------------------------------------

def send_meeting_invitation_email(meeting, participant):
    """Send meeting invitation email"""
    subject = f"Meeting Invitation: {meeting.title}"
    
    join_url = url_for('meeting_join_page', meeting_room_id=meeting.meeting_room_id, _external=True)
    
    text_body = f"""
Hi {participant.user.name},

You've been invited to a meeting on InnoBridge!

Meeting Details:
- Title: {meeting.title}
- Date: {meeting.scheduled_at.strftime('%B %d, %Y')}
- Time: {meeting.scheduled_at.strftime('%I:%M %p')}
- Duration: {meeting.duration} minutes

Description:
{meeting.description or 'No description provided'}

Join the meeting:
{join_url}

See you there!

Best regards,
The InnoBridge Team

---
This is an automated message. Please do not reply to this email.
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .meeting-box {{ background: white; padding: 20px; border-left: 4px solid #667eea; margin: 20px 0; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📅 Meeting Invitation</h1>
        </div>
        <div class="content">
            <p>Hi <strong>{participant.user.name}</strong>,</p>
            
            <p>You've been invited to a meeting on InnoBridge!</p>
            
            <div class="meeting-box">
                <h2>{meeting.title}</h2>
                <p><strong>📅 Date:</strong> {meeting.scheduled_at.strftime('%B %d, %Y')}</p>
                <p><strong>🕐 Time:</strong> {meeting.scheduled_at.strftime('%I:%M %p')}</p>
                <p><strong>⏱️ Duration:</strong> {meeting.duration} minutes</p>
                {f'<p><strong>📝 Description:</strong><br>{meeting.description}</p>' if meeting.description else ''}
            </div>
            
            <center>
                <a href="{join_url}" class="button">Join Meeting</a>
            </center>
            
            <p>See you there!</p>
            
            <p>Best regards,<br><strong>The InnoBridge Team</strong></p>
        </div>
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
"""
    
    return send_email(subject, participant.user.email, text_body, html_body)


def send_meeting_reminder_email(meeting, participant):
    """Send meeting reminder email (24 hours before)"""
    subject = f"Reminder: Meeting Tomorrow - {meeting.title}"
    
    join_url = url_for('meeting_join_page', meeting_room_id=meeting.meeting_room_id, _external=True)
    
    text_body = f"""
Hi {participant.user.name},

This is a reminder about your upcoming meeting tomorrow!

Meeting Details:
- Title: {meeting.title}
- Date: {meeting.scheduled_at.strftime('%B %d, %Y')}
- Time: {meeting.scheduled_at.strftime('%I:%M %p')}
- Duration: {meeting.duration} minutes

Join the meeting:
{join_url}

See you there!

Best regards,
The InnoBridge Team

---
This is an automated message. Please do not reply to this email.
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #ffc107; color: #333; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .meeting-box {{ background: white; padding: 20px; border-left: 4px solid #ffc107; margin: 20px 0; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⏰ Meeting Reminder</h1>
        </div>
        <div class="content">
            <p>Hi <strong>{participant.user.name}</strong>,</p>
            
            <p>This is a reminder about your upcoming meeting <strong>tomorrow</strong>!</p>
            
            <div class="meeting-box">
                <h2>{meeting.title}</h2>
                <p><strong>📅 Date:</strong> {meeting.scheduled_at.strftime('%B %d, %Y')}</p>
                <p><strong>🕐 Time:</strong> {meeting.scheduled_at.strftime('%I:%M %p')}</p>
                <p><strong>⏱️ Duration:</strong> {meeting.duration} minutes</p>
            </div>
            
            <center>
                <a href="{join_url}" class="button">Join Meeting</a>
            </center>
            
            <p>See you there!</p>
            
            <p>Best regards,<br><strong>The InnoBridge Team</strong></p>
        </div>
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
"""
    
    return send_email(subject, participant.user.email, text_body, html_body)


def send_meeting_cancelled_email(meeting, participant):
    """Send meeting cancellation email"""
    subject = f"Meeting Cancelled: {meeting.title}"
    
    text_body = f"""
Hi {participant.user.name},

The following meeting has been cancelled:

Meeting Details:
- Title: {meeting.title}
- Date: {meeting.scheduled_at.strftime('%B %d, %Y')}
- Time: {meeting.scheduled_at.strftime('%I:%M %p')}

We apologize for any inconvenience.

Best regards,
The InnoBridge Team

---
This is an automated message. Please do not reply to this email.
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #dc3545; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .meeting-box {{ background: white; padding: 20px; border-left: 4px solid #dc3545; margin: 20px 0; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>❌ Meeting Cancelled</h1>
        </div>
        <div class="content">
            <p>Hi <strong>{participant.user.name}</strong>,</p>
            
            <p>The following meeting has been <strong>cancelled</strong>:</p>
            
            <div class="meeting-box">
                <h2>{meeting.title}</h2>
                <p><strong>📅 Date:</strong> {meeting.scheduled_at.strftime('%B %d, %Y')}</p>
                <p><strong>🕐 Time:</strong> {meeting.scheduled_at.strftime('%I:%M %p')}</p>
            </div>
            
            <p>We apologize for any inconvenience.</p>
            
            <p>Best regards,<br><strong>The InnoBridge Team</strong></p>
        </div>
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
"""
    
    return send_email(subject, participant.user.email, text_body, html_body)


# -----------------------------------------
# APPLICATION STATUS EMAILS
# -----------------------------------------

def send_application_received_email(application):
    """Send confirmation email when application is received"""
    subject = f"Application Received: {application.opportunity.title}"
    
    text_body = f"""
Hi {application.startup.founder.name},

Thank you for applying to {application.opportunity.title}!

Your application has been successfully received and is now under review.

Application Details:
- Opportunity: {application.opportunity.title}
- Startup: {application.startup.name}
- Submitted: {application.created_at.strftime('%B %d, %Y at %I:%M %p')}
- Status: {application.status.capitalize()}

We'll notify you once there's an update on your application status.

Best regards,
The InnoBridge Team

---
This is an automated message. Please do not reply to this email.
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #28a745; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .info-box {{ background: white; padding: 20px; border-left: 4px solid #28a745; margin: 20px 0; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ Application Received</h1>
        </div>
        <div class="content">
            <p>Hi <strong>{application.startup.founder.name}</strong>,</p>
            
            <p>Thank you for applying to <strong>{application.opportunity.title}</strong>!</p>
            
            <p>Your application has been successfully received and is now under review.</p>
            
            <div class="info-box">
                <strong>Application Details:</strong><br>
                📋 Opportunity: {application.opportunity.title}<br>
                🚀 Startup: {application.startup.name}<br>
                📅 Submitted: {application.created_at.strftime('%B %d, %Y at %I:%M %p')}<br>
                📊 Status: {application.status.capitalize()}
            </div>
            
            <p>We'll notify you once there's an update on your application status.</p>
            
            <p>Best regards,<br><strong>The InnoBridge Team</strong></p>
        </div>
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
"""
    
    return send_email(subject, application.startup.founder.email, text_body, html_body)


def send_application_status_update_email(application):
    """Send email when application status changes"""
    subject = f"Application Update: {application.opportunity.title}"
    
    status_messages = {
        'accepted': '🎉 Congratulations! Your application has been accepted!',
        'rejected': 'Unfortunately, your application was not selected this time.',
        'shortlisted': '🌟 Great news! Your application has been shortlisted!',
        'under_review': 'Your application is currently under review.'
    }
    
    status_message = status_messages.get(application.status, 'Your application status has been updated.')
    
    text_body = f"""
Hi {application.startup.founder.name},

{status_message}

Application Details:
- Opportunity: {application.opportunity.title}
- Startup: {application.startup.name}
- New Status: {application.status.capitalize()}

{f'Feedback: {application.feedback}' if application.feedback else ''}

Thank you for your interest in InnoBridge opportunities.

Best regards,
The InnoBridge Team

---
This is an automated message. Please do not reply to this email.
"""
    
    status_colors = {
        'accepted': '#28a745',
        'rejected': '#dc3545',
        'shortlisted': '#ffc107',
        'under_review': '#17a2b8'
    }
    
    status_color = status_colors.get(application.status, '#667eea')
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: {status_color}; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .info-box {{ background: white; padding: 20px; border-left: 4px solid {status_color}; margin: 20px 0; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📬 Application Update</h1>
        </div>
        <div class="content">
            <p>Hi <strong>{application.startup.founder.name}</strong>,</p>
            
            <p>{status_message}</p>
            
            <div class="info-box">
                <strong>Application Details:</strong><br>
                📋 Opportunity: {application.opportunity.title}<br>
                🚀 Startup: {application.startup.name}<br>
                📊 New Status: <strong>{application.status.capitalize()}</strong>
            </div>
            
            {f'<div class="info-box"><strong>Feedback:</strong><br>{application.feedback}</div>' if application.feedback else ''}
            
            <p>Thank you for your interest in InnoBridge opportunities.</p>
            
            <p>Best regards,<br><strong>The InnoBridge Team</strong></p>
        </div>
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
"""
    
    return send_email(subject, application.startup.founder.email, text_body, html_body)


# -----------------------------------------
# REFERRAL EMAILS
# -----------------------------------------

def send_referral_notification_email(referral):
    """Send email when someone uses a referral link"""
    subject = "Someone Used Your Referral Link! 🎉"
    
    text_body = f"""
Hi {referral.referrer.name},

Great news! Someone just used your referral link to sign up for InnoBridge!

Referral Details:
- Referred Startup: {referral.startup_name or 'Pending signup'}
- Status: {referral.status.capitalize()}
- Date: {referral.created_at.strftime('%B %d, %Y')}

Keep sharing your referral link to help grow the InnoBridge community!

Your Referral Link:
{url_for('index', _external=True)}?ref={referral.token}

Best regards,
The InnoBridge Team

---
This is an automated message. Please do not reply to this email.
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .info-box {{ background: white; padding: 20px; border-left: 4px solid #667eea; margin: 20px 0; }}
        .referral-link {{ background: #f0f0f0; padding: 15px; border-radius: 5px; word-break: break-all; font-family: monospace; }}
        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Referral Success!</h1>
        </div>
        <div class="content">
            <p>Hi <strong>{referral.referrer.name}</strong>,</p>
            
            <p>Great news! Someone just used your referral link to sign up for InnoBridge!</p>
            
            <div class="info-box">
                <strong>Referral Details:</strong><br>
                🚀 Referred Startup: {referral.startup_name or 'Pending signup'}<br>
                📊 Status: {referral.status.capitalize()}<br>
                📅 Date: {referral.created_at.strftime('%B %d, %Y')}
            </div>
            
            <p>Keep sharing your referral link to help grow the InnoBridge community!</p>
            
            <p><strong>Your Referral Link:</strong></p>
            <div class="referral-link">
                {url_for('index', _external=True)}?ref={referral.token}
            </div>
            
            <p>Best regards,<br><strong>The InnoBridge Team</strong></p>
        </div>
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
"""
    
    return send_email(subject, referral.referrer.email, text_body, html_body)


# -----------------------------------------
# UTILITY FUNCTIONS
# -----------------------------------------

def is_email_configured():
    """Check if email is properly configured"""
    return bool(current_app.config.get('MAIL_USERNAME'))


def test_email_connection():
    """Test email server connection"""
    try:
        with mail.connect() as conn:
            print("✅ Email server connection successful")
            return True
    except Exception as e:
        print(f"❌ Email server connection failed: {e}")
        return False
