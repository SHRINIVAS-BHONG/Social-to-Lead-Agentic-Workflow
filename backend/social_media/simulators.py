"""
simulators.py – Mock social media platform simulators.

Each simulator fakes the full posting workflow:
  connect → authenticate → prepare content → upload → publish → verify

No real API calls are made. All responses are realistic-looking mock data.
"""

import asyncio
import random
import uuid
from datetime import datetime
from typing import AsyncGenerator


# ─────────────────────────────────────────────────────────────────────────────
# Demo content per platform
# ─────────────────────────────────────────────────────────────────────────────

DEMO_CONTENT = {
    "Instagram": {
        "caption": "🎬 Just automated my entire video editing workflow with AutoStream AI! From raw footage to polished reel in minutes. Game changer for content creators. #AutoStream #ContentCreator #VideoEditing #AI #Instagram",
        "hashtags": ["#AutoStream", "#ContentCreator", "#VideoEditing", "#AI", "#Reels"],
        "media_type": "Reel (15s)",
        "resolution": "1080×1920",
        "thumbnail": "autostream_reel_thumbnail.jpg",
        "mock_post_id": f"IG_{uuid.uuid4().hex[:10].upper()}",
        "mock_url": "https://instagram.com/p/mock_autostream_post",
        "likes": random.randint(800, 3500),
        "comments": random.randint(40, 200),
        "shares": random.randint(100, 600),
        "reach": random.randint(3000, 15000),
    },
    "TikTok": {
        "caption": "POV: You discover AutoStream and your editing time drops by 90% 🚀 #AutoStream #VideoEditing #ContentHack #TikTokMadeMeDoIt #AI",
        "hashtags": ["#AutoStream", "#VideoEditing", "#ContentHack", "#AI", "#FYP"],
        "media_type": "Video (30s)",
        "resolution": "1080×1920",
        "sound": "Original Sound – AutoStream",
        "effects": ["Auto-captions", "Trending transition"],
        "mock_post_id": f"TT_{uuid.uuid4().hex[:10].upper()}",
        "mock_url": "https://tiktok.com/@user/video/mock_autostream",
        "likes": random.randint(5000, 50000),
        "comments": random.randint(200, 1500),
        "shares": random.randint(500, 5000),
        "views": random.randint(20000, 200000),
    },
    "YouTube": {
        "title": "How I Edit Videos 10x Faster with AutoStream AI (Full Workflow)",
        "description": "In this video I walk through my entire AutoStream AI video editing workflow that saves me hours every week...",
        "tags": ["video editing", "AI tools", "AutoStream", "content creation", "productivity"],
        "media_type": "Video (8:45)",
        "resolution": "1920×1080",
        "thumbnail": "autostream_yt_thumbnail.jpg",
        "mock_post_id": f"YT_{uuid.uuid4().hex[:10].upper()}",
        "mock_url": "https://youtube.com/watch?v=mock_autostream",
        "likes": random.randint(1000, 8000),
        "comments": random.randint(100, 500),
        "views": random.randint(5000, 50000),
        "subscribers_gained": random.randint(20, 150),
    },
}

POSTING_STAGES = {
    "Instagram": [
        ("🔗 Connecting to Instagram API...", 1.2),
        ("🔐 Authenticating account...", 1.0),
        ("📝 Preparing caption & hashtags...", 0.8),
        ("📤 Uploading media file...", 2.0),
        ("🚀 Publishing post...", 1.5),
        ("✅ Verifying publication...", 0.8),
    ],
    "TikTok": [
        ("🔗 Connecting to TikTok API...", 1.2),
        ("🔐 Authenticating account...", 1.0),
        ("🎵 Adding trending sound...", 0.8),
        ("✨ Applying effects & captions...", 1.2),
        ("📤 Uploading video...", 2.5),
        ("🚀 Publishing to For You Page...", 1.5),
        ("✅ Post live! Tracking engagement...", 0.8),
    ],
    "YouTube": [
        ("🔗 Connecting to YouTube Data API...", 1.2),
        ("🔐 Authenticating via OAuth...", 1.0),
        ("🖼️ Uploading thumbnail...", 0.8),
        ("📝 Setting title, description & tags...", 0.8),
        ("📤 Uploading video file...", 3.0),
        ("⚙️ Processing video (HD)...", 2.0),
        ("🚀 Publishing to channel...", 1.0),
        ("✅ Video live! Notifying subscribers...", 0.8),
    ],
}

MOCK_ACCOUNTS = {
    "Instagram": {
        "username": "@your_channel",
        "followers": f"{random.randint(1, 50)}.{random.randint(1, 9)}K",
        "verified": False,
        "account_type": "Creator",
    },
    "TikTok": {
        "username": "@your_channel",
        "followers": f"{random.randint(1, 100)}.{random.randint(1, 9)}K",
        "verified": False,
        "account_type": "Creator",
    },
    "YouTube": {
        "channel_name": "Your Channel",
        "subscribers": f"{random.randint(1, 50)}.{random.randint(1, 9)}K",
        "verified": False,
        "account_type": "Content Creator",
    },
}


async def simulate_posting(platform: str) -> AsyncGenerator[dict, None]:
    """
    Async generator that yields real-time posting stage events for a platform.

    Yields dicts with keys:
      type: 'stage' | 'complete' | 'error'
      stage: current stage label
      stage_index: 0-based index
      total_stages: total number of stages
      progress: 0-100 float
      account: mock account info (on first stage)
      result: final post data (on complete)
    """
    stages = POSTING_STAGES.get(platform, POSTING_STAGES["Instagram"])
    account = MOCK_ACCOUNTS.get(platform, {})
    total = len(stages)

    for i, (label, delay) in enumerate(stages):
        progress = round(((i + 1) / total) * 100)
        event = {
            "type": "posting_stage",
            "platform": platform,
            "stage": label,
            "stage_index": i,
            "total_stages": total,
            "progress": progress,
        }
        if i == 0:
            event["account"] = account

        yield event
        await asyncio.sleep(delay)

    # Final result
    content = DEMO_CONTENT.get(platform, {})
    yield {
        "type": "posting_complete",
        "platform": platform,
        "progress": 100,
        "result": {
            "post_id": content.get("mock_post_id", f"POST_{uuid.uuid4().hex[:8].upper()}"),
            "post_url": content.get("mock_url", "#"),
            "content": content,
            "posted_at": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
        },
    }
