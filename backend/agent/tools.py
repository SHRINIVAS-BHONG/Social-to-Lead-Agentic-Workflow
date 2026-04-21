import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# In-memory log of captured leads (simulates a CRM / DB)
captured_leads: list[dict] = []


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

    log_msg = (
        f"[LEAD CAPTURED] {timestamp} | "
        f"Name: {name} | Email: {email} | Platform: {platform}"
    )
    print(log_msg)
    logger.info(log_msg)

    return {
        "status": "success",
        "message": f"Lead captured successfully: {name}, {email}, {platform}",
        "data": lead_record,
    }


def get_all_leads() -> list[dict]:
    """Return all captured leads (for admin/logging purposes)."""
    return captured_leads
