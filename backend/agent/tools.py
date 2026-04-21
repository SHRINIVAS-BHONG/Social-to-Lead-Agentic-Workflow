from datetime import datetime
from config.logging_config import get_logger
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

logger = get_logger(__name__)

# In-memory log of captured leads (simulates a CRM / DB)
captured_leads: list[dict] = []




def send_welcome_email(name: str, email: str, platform: str) -> bool:
    """
    Send a welcome email to the captured lead.
    
    This function sends an automated welcome email using SMTP.
    In production, you would use:
      - SendGrid API
      - AWS SES
      - Mailgun
      - Postmark
    
    Args:
        name: Lead's full name
        email: Lead's email address
        platform: Content platform (YouTube, Instagram, etc.)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Get SMTP configuration from environment variables
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        from_email = os.getenv("FROM_EMAIL", smtp_user)
        
        # Skip email sending if SMTP not configured
        if not smtp_user or not smtp_password:
            logger.warning(
                "SMTP not configured - email not sent",
                extra={"lead_email": email}
            )
            return False
        
        # Create email message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Welcome to AutoStream Pro! 🎬"
        msg["From"] = from_email
        msg["To"] = email
        
        # Email body (HTML version)
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <h2 style="color: #6366f1;">Welcome to AutoStream, {name}! 🎉</h2>
              
              <p>Thank you for your interest in AutoStream Pro!</p>
              
              <p>We're excited to help you create amazing content for your <strong>{platform}</strong> channel with our AI-powered video editing tools.</p>
              
              <h3 style="color: #6366f1;">What's Next?</h3>
              <ul>
                <li>Our team will reach out within 24 hours to set up your account</li>
                <li>You'll get access to our 7-day free trial (no credit card required)</li>
                <li>We'll provide personalized onboarding for your {platform} workflow</li>
              </ul>
              
              <h3 style="color: #6366f1;">AutoStream Pro Features:</h3>
              <ul>
                <li>✅ Unlimited videos per month</li>
                <li>✅ 4K resolution export</li>
                <li>✅ AI-generated captions and subtitles</li>
                <li>✅ Advanced editing tools</li>
                <li>✅ Priority 24/7 support</li>
              </ul>
              
              <p style="margin-top: 30px;">
                <a href="https://autostream.example.com/dashboard" 
                   style="background-color: #6366f1; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                  Get Started Now
                </a>
              </p>
              
              <p style="margin-top: 30px; color: #666; font-size: 14px;">
                Questions? Reply to this email or contact us at support@autostream.example.com
              </p>
              
              <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
              
              <p style="color: #999; font-size: 12px;">
                AutoStream - AI-Powered Video Editing for Content Creators<br>
                You're receiving this email because you signed up for AutoStream Pro.
              </p>
            </div>
          </body>
        </html>
        """
        
        # Plain text version (fallback)
        text_body = f"""
        Welcome to AutoStream, {name}!
        
        Thank you for your interest in AutoStream Pro!
        
        We're excited to help you create amazing content for your {platform} channel 
        with our AI-powered video editing tools.
        
        What's Next?
        - Our team will reach out within 24 hours to set up your account
        - You'll get access to our 7-day free trial (no credit card required)
        - We'll provide personalized onboarding for your {platform} workflow
        
        AutoStream Pro Features:
        - Unlimited videos per month
        - 4K resolution export
        - AI-generated captions and subtitles
        - Advanced editing tools
        - Priority 24/7 support
        
        Questions? Reply to this email or contact us at support@autostream.example.com
        
        ---
        AutoStream - AI-Powered Video Editing for Content Creators
        """
        
        # Attach both versions
        part1 = MIMEText(text_body, "plain")
        part2 = MIMEText(html_body, "html")
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email via SMTP
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        logger.info(
            "Welcome email sent successfully",
            extra={
                "lead_name": name,
                "lead_email": email,
                "lead_platform": platform
            }
        )
        return True
        
    except Exception as e:
        logger.error(
            "Failed to send welcome email",
            extra={
                "error": str(e),
                "lead_email": email
            },
            exc_info=True
        )
        return False


def mock_lead_capture(name: str, email: str, platform: str) -> dict:
    """
    Mock API that simulates capturing a lead into a CRM system.
    
    In production this would:
      - POST to a CRM REST API (HubSpot, Salesforce, etc.)
      - Send a Slack notification to the sales team
      - Trigger an automated welcome email

    Args:
        name: Full name of the lead
        email: Email address of the lead
        platform: Content platform (YouTube, Instagram, TikTok, etc.)

    Returns:
        dict with status and captured data
    """
    timestamp = datetime.now().isoformat()

    lead_record = {
        "name": name,
        "email": email,
        "platform": platform,
        "captured_at": timestamp,
        "source": "AutoStream AI Agent",
    }

    captured_leads.append(lead_record)

    logger.info(
        "Lead captured successfully",
        extra={
            "lead_name": name,
            "lead_email": email,
            "lead_platform": platform,
            "timestamp": timestamp,
        }
    )

    # Send welcome email (async in production)
    email_sent = send_welcome_email(name, email, platform)

    return {
        "status": "success",
        "message": f"Lead captured successfully: {name}, {email}, {platform}",
        "data": lead_record,
        "email_sent": email_sent,
    }


def get_all_leads() -> list[dict]:
    """Return all captured leads (for admin/logging purposes)."""
    return captured_leads
