"""
tools.py – Real LangChain-compatible agentic tools for social media posting.

These are proper @tool decorated functions that the LLM can reason about
and call autonomously. The LLM decides WHICH tool to call, WHEN, and with
WHAT arguments — this is real tool-calling, not scripted simulation.
"""

import asyncio
import random
import uuid
from datetime import datetime
from langchain.tools import tool
from backend.config.logging_config import get_logger

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Tool 1 – Connect to platform
# ─────────────────────────────────────────────────────────────────────────────

@tool
def connect_to_platform(platform: str) -> dict:
    """
    Connect and authenticate to a social media platform.
    Use this FIRST before posting. Supports: Instagram, TikTok, YouTube.
    Returns connection status and mock account details.
    """
    platform = platform.strip()
    supported = {"Instagram", "TikTok", "YouTube"}

    if platform not in supported:
        return {
            "success": False,
            "error": f"Platform '{platform}' not supported. Choose from: {', '.join(supported)}",
        }

    # Simulate realistic auth delay
    accounts = {
        "Instagram": {
            "username": "@autostream_demo",
            "followers": f"{random.randint(5, 50)}.{random.randint(1,9)}K",
            "account_type": "Creator Account",
            "auth_method": "OAuth 2.0",
        },
        "TikTok": {
            "username": "@autostream_demo",
            "followers": f"{random.randint(10, 100)}.{random.randint(1,9)}K",
            "account_type": "Creator Account",
            "auth_method": "TikTok Login Kit",
        },
        "YouTube": {
            "channel_name": "AutoStream Demo Channel",
            "subscribers": f"{random.randint(1, 20)}.{random.randint(1,9)}K",
            "account_type": "Content Creator",
            "auth_method": "Google OAuth 2.0",
        },
    }

    logger.info(f"[TOOL] connect_to_platform called: {platform}")

    return {
        "success": True,
        "platform": platform,
        "connected": True,
        "account": accounts[platform],
        "message": f"Successfully connected to {platform} via {accounts[platform]['auth_method']}",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Tool 2 – Generate platform-specific content
# ─────────────────────────────────────────────────────────────────────────────

@tool
def generate_post_content(platform: str, topic: str = "AutoStream AI video editing") -> dict:
    """
    Generate platform-optimized post content for the given platform and topic.
    Call this AFTER connecting to the platform to prepare content before posting.
    Returns caption, hashtags, media specs, and content strategy.
    """
    platform = platform.strip()

    content_templates = {
        "Instagram": {
            "caption": f"🎬 Just transformed my entire content workflow with AutoStream AI! "
                       f"What used to take hours now takes minutes. "
                       f"If you're a creator on {platform}, this is a game-changer. "
                       f"Link in bio to try it free! ✨",
            "hashtags": ["#AutoStream", "#ContentCreator", "#VideoEditing", "#AITools",
                         "#InstagramReels", "#CreatorEconomy", "#VideoContent"],
            "media_type": "Reel",
            "duration": "15-30 seconds",
            "resolution": "1080×1920 (9:16)",
            "best_time": "6-9 PM local time",
            "strategy": "Hook in first 3 seconds, show before/after transformation",
        },
        "TikTok": {
            "caption": f"POV: You find AutoStream and your editing time drops 90% 🚀 "
                       f"#AutoStream #VideoEditing #ContentHack #AITools #FYP",
            "hashtags": ["#AutoStream", "#VideoEditing", "#ContentHack", "#AITools",
                         "#FYP", "#TikTokMadeMeDoIt", "#CreatorTips"],
            "media_type": "Short Video",
            "duration": "15-60 seconds",
            "resolution": "1080×1920 (9:16)",
            "sound": "Trending audio recommended",
            "best_time": "7-9 AM or 7-11 PM",
            "strategy": "Use trending sound, text overlay, fast cuts",
        },
        "YouTube": {
            "title": "I Used AI to Edit ALL My Videos for 30 Days (AutoStream Review)",
            "description": f"In this video, I test AutoStream AI for 30 days straight "
                           f"and show you exactly how it changed my workflow...\n\n"
                           f"🔗 Try AutoStream free: https://autostream.example.com\n\n"
                           f"Timestamps:\n0:00 Intro\n1:30 Setup\n3:00 First test\n"
                           f"6:00 Results\n8:00 Final verdict",
            "tags": ["AutoStream", "AI video editing", "content creation",
                     "YouTube automation", "video editing tutorial"],
            "thumbnail_concept": "Split screen: messy timeline vs clean AutoStream output",
            "media_type": "Long-form Video",
            "duration": "8-12 minutes",
            "resolution": "1920×1080 (16:9)",
            "best_time": "2-4 PM Thursday/Friday",
            "strategy": "Strong thumbnail + title, chapters for retention",
        },
    }

    if platform not in content_templates:
        return {"success": False, "error": f"No content template for platform: {platform}"}

    content = content_templates[platform]
    logger.info(f"[TOOL] generate_post_content called: platform={platform}, topic={topic}")

    return {
        "success": True,
        "platform": platform,
        "topic": topic,
        "content": content,
        "message": f"Generated optimized {platform} content ready for posting",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Tool 3 – Post to platform
# ─────────────────────────────────────────────────────────────────────────────

@tool
def post_to_platform(platform: str, content_summary: str) -> dict:
    """
    Publish the prepared content to the social media platform.
    Call this AFTER generate_post_content. Requires platform connection.
    Returns post ID, URL, and initial engagement metrics.
    """
    platform = platform.strip()
    post_id_prefixes = {"Instagram": "IG", "TikTok": "TT", "YouTube": "YT"}

    if platform not in post_id_prefixes:
        return {"success": False, "error": f"Cannot post to unsupported platform: {platform}"}

    prefix = post_id_prefixes[platform]
    post_id = f"{prefix}_{uuid.uuid4().hex[:12].upper()}"

    # Platform-specific mock metrics
    metrics = {
        "Instagram": {
            "initial_likes": random.randint(50, 300),
            "initial_comments": random.randint(5, 40),
            "initial_reach": random.randint(500, 3000),
            "post_url": f"https://instagram.com/p/{uuid.uuid4().hex[:11]}",
        },
        "TikTok": {
            "initial_views": random.randint(500, 5000),
            "initial_likes": random.randint(100, 1000),
            "initial_shares": random.randint(20, 200),
            "post_url": f"https://tiktok.com/@autostream_demo/video/{random.randint(10**17, 10**18)}",
        },
        "YouTube": {
            "initial_views": random.randint(50, 500),
            "initial_likes": random.randint(10, 100),
            "video_url": f"https://youtube.com/watch?v={uuid.uuid4().hex[:11]}",
            "processing_status": "HD processing complete",
        },
    }

    result_metrics = metrics[platform]
    url_key = "video_url" if platform == "YouTube" else "post_url"
    post_url = result_metrics.get(url_key, result_metrics.get("post_url", "#"))

    logger.info(f"[TOOL] post_to_platform called: platform={platform}, post_id={post_id}")

    return {
        "success": True,
        "platform": platform,
        "post_id": post_id,
        "post_url": post_url,
        "posted_at": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
        "metrics": result_metrics,
        "content_summary": content_summary,
        "message": f"✅ Successfully published to {platform}! Post ID: {post_id}",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Tool 4 – Check post analytics
# ─────────────────────────────────────────────────────────────────────────────

@tool
def check_post_analytics(platform: str, post_id: str) -> dict:
    """
    Check the performance analytics of a published post.
    Call this AFTER posting to get engagement metrics and insights.
    Returns views, likes, comments, shares, and AI-generated insights.
    """
    platform = platform.strip()

    analytics = {
        "Instagram": {
            "views": random.randint(2000, 15000),
            "likes": random.randint(800, 3500),
            "comments": random.randint(40, 200),
            "shares": random.randint(100, 600),
            "saves": random.randint(200, 1000),
            "reach": random.randint(3000, 15000),
            "profile_visits": random.randint(100, 500),
            "engagement_rate": f"{random.uniform(3.5, 8.2):.1f}%",
        },
        "TikTok": {
            "views": random.randint(20000, 200000),
            "likes": random.randint(5000, 50000),
            "comments": random.randint(200, 1500),
            "shares": random.randint(500, 5000),
            "average_watch_time": f"{random.randint(8, 25)}s",
            "completion_rate": f"{random.randint(45, 75)}%",
            "for_you_page_reach": f"{random.randint(60, 90)}%",
            "engagement_rate": f"{random.uniform(8.0, 18.5):.1f}%",
        },
        "YouTube": {
            "views": random.randint(5000, 50000),
            "likes": random.randint(1000, 8000),
            "comments": random.randint(100, 500),
            "subscribers_gained": random.randint(20, 150),
            "average_view_duration": f"{random.randint(3, 7)}:{random.randint(10,59):02d}",
            "click_through_rate": f"{random.uniform(4.0, 9.5):.1f}%",
            "impressions": random.randint(20000, 100000),
            "engagement_rate": f"{random.uniform(5.0, 12.0):.1f}%",
        },
    }

    if platform not in analytics:
        return {"success": False, "error": f"No analytics available for: {platform}"}

    platform_analytics = analytics[platform]

    # AI insight based on metrics
    engagement = float(platform_analytics["engagement_rate"].replace("%", ""))
    if engagement > 10:
        insight = "🔥 Exceptional performance! This post is going viral. Consider boosting it."
    elif engagement > 6:
        insight = "📈 Strong engagement. Your audience resonates with this content style."
    else:
        insight = "💡 Good start. Try posting at peak hours and engaging with early comments."

    logger.info(f"[TOOL] check_post_analytics called: platform={platform}, post_id={post_id}")

    return {
        "success": True,
        "platform": platform,
        "post_id": post_id,
        "analytics": platform_analytics,
        "ai_insight": insight,
        "message": f"Analytics retrieved for {platform} post {post_id}",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Export all tools as a list for the agent
# ─────────────────────────────────────────────────────────────────────────────

SOCIAL_MEDIA_TOOLS = [
    connect_to_platform,
    generate_post_content,
    post_to_platform,
    check_post_analytics,
]
