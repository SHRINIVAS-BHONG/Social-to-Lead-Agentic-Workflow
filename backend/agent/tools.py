from datetime import datetime
from backend.config.logging_config import get_logger
from backend.auth.store import create_pending_user
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

logger = get_logger(__name__)

# In-memory log of captured leads (simulates a CRM / DB)
captured_leads: list[dict] = []




def send_welcome_email(name: str, email: str, platform: str, reg_token: str = "") -> bool:
    """Send a welcome email with a registration link to activate the account."""
    try:
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        from_email = os.getenv("FROM_EMAIL", smtp_user)
        website_url = os.getenv("WEBSITE_URL", "http://localhost:3000")

        if not smtp_user or not smtp_password:
            logger.warning("SMTP not configured - email not sent", extra={"lead_email": email})
            return False

        # Build registration link with token
        register_url = f"{website_url}/register/{reg_token}" if reg_token else website_url

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Welcome to AutoStream Pro! 🎬 — Activate Your Account"
        msg["From"] = from_email
        msg["To"] = email

        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <h2 style="color: #6366f1;">Welcome to AutoStream, {name}! 🎉</h2>
              <p>Thank you for your interest in AutoStream Pro!</p>
              <p>We're excited to help you create amazing content for your <strong>{platform}</strong> channel with our AI-powered video editing tools.</p>

              <h3 style="color: #6366f1;">What's Next?</h3>
              <ul>
                <li>Click <strong>Activate My Account</strong> below to set your password</li>
                <li>Connect your {platform} account to AutoStream</li>
                <li>Start your 7-day free trial (no credit card required)</li>
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
                <a href="{register_url}"
                   style="background-color: #6366f1; color: white; padding: 14px 28px;
                          text-decoration: none; border-radius: 8px; display: inline-block;
                          font-weight: bold; font-size: 16px;">
                  🚀 Activate My Account
                </a>
              </p>
              <p style="color: #999; font-size: 12px; margin-top: 10px;">
                This link is unique to you. Do not share it.
              </p>

              <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
              <p style="color: #999; font-size: 12px;">
                AutoStream - AI-Powered Video Editing for Content Creators<br>
                Questions? Contact us at support@autostream.example.com
              </p>
            </div>
          </body>
        </html>
        """

        text_body = f"Welcome {name}! Activate your AutoStream account: {register_url}"

        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        logger.info("Welcome email sent", extra={"lead_name": name, "lead_email": email})
        return True

    except Exception as e:
        logger.error("Failed to send welcome email", extra={"error": str(e), "lead_email": email}, exc_info=True)
        return False


def mock_lead_capture(name: str, email: str, platform: str) -> dict:
    """Capture lead, create pending user, send activation email."""
    timestamp = datetime.now().isoformat()

    lead_record = {
        "name": name,
        "email": email,
        "platform": platform,
        "captured_at": timestamp,
        "source": "AutoStream AI Agent",
    }
    captured_leads.append(lead_record)

    logger.info("Lead captured", extra={"lead_name": name, "lead_email": email, "lead_platform": platform})

    # Create pending user and get registration token
    reg_token = create_pending_user(name, email, platform)

    # Send welcome email with activation link
    email_sent = send_welcome_email(name, email, platform, reg_token)

    return {
        "status": "success",
        "message": f"Lead captured: {name}, {email}, {platform}",
        "data": lead_record,
        "email_sent": email_sent,
        "reg_token": reg_token,
    }


def get_all_leads() -> list[dict]:
    """Return all captured leads (for admin/logging purposes)."""
    return captured_leads
