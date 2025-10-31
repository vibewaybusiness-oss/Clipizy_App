"""
Social Media Automation Pipeline Service
Handles YouTube, TikTok, and Instagram API integrations with automated publishing
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
from sqlalchemy.orm import Session

from api.models import Export, SocialAccount, Stats
from api.services.storage import backend_storage_service

logger = logging.getLogger(__name__)


class SocialMediaService:
    def __init__(self, backend_storage_service):
        self.backend_storage_service = backend_storage_service
        self.platform_apis = {"youtube": YouTubeAPI(), "tiktok": TikTokAPI(), "instagram": InstagramAPI()}

    async def connect_account(
        self, db: Session, user_id: str, platform: str, auth_data: Dict[str, Any]
    ) -> SocialAccount:
        """Connect a social media account via OAuth"""
        try:
            # Get platform-specific account info
            api = self.platform_apis[platform]
            account_info = await api.get_account_info(auth_data["access_token"])

            # Store in database
            social_account = SocialAccount(
                id=uuid.uuid4(),
                user_id=user_id,
                platform=platform,
                account_name=account_info["name"],
                account_id=account_info["id"],
                access_token=auth_data["access_token"],
                refresh_token=auth_data.get("refresh_token"),
                expires_at=datetime.utcnow() + timedelta(seconds=auth_data.get("expires_in", 3600)),
            )

            db.add(social_account)
            db.commit()
            db.refresh(social_account)

            logger.info(f"Connected {platform} account for user {user_id}")
            return social_account

        except Exception as e:
            logger.error(f"Failed to connect {platform} account: {e}")
            raise

    async def publish_video(
        self, db: Session, export: Export, platform: str, user_id: str, publish_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Publish a video to a social media platform"""
        try:
            # Get user's social account for platform
            social_account = (
                db.query(SocialAccount)
                .filter(SocialAccount.user_id == user_id, SocialAccount.platform == platform)
                .first()
            )

            if not social_account:
                raise ValueError(f"No {platform} account connected for user {user_id}")

            # Refresh token if needed
            await self._refresh_token_if_needed(db, social_account)

            # Get platform API
            api = self.platform_apis[platform]

            # Upload video
            video_url = await self._get_video_url(export.file_path)
            result = await api.upload_video(
                access_token=social_account.access_token,
                video_url=video_url,
                title=publish_options.get("title", ""),
                description=publish_options.get("description", ""),
                tags=publish_options.get("tags", []),
                privacy=publish_options.get("privacy", "public"),
                thumbnail_url=publish_options.get("thumbnail_url"),
            )

            # Store external ID for tracking
            external_id = result["id"]

            # Create stats entry
            stats = Stats(
                id=uuid.uuid4(),
                export_id=export.id,
                project_id=export.project_id,
                user_id=user_id,
                platform=platform,
                external_id=external_id,
                views=0,
                likes=0,
                comments=0,
                shares=0,
                fetched_at=datetime.utcnow(),
            )
            db.add(stats)
            db.commit()

            # Schedule analytics fetching
            asyncio.create_task(self._schedule_analytics_fetch(db, stats))

            logger.info(f"Published video {export.id} to {platform} as {external_id}")
            return {
                "success": True,
                "platform": platform,
                "external_id": external_id,
                "url": result.get("url"),
                "published_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to publish video to {platform}: {e}")
            return {"success": False, "error": str(e), "platform": platform}

    async def batch_publish(
        self, db: Session, export: Export, platforms: List[str], user_id: str, publish_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Publish video to multiple platforms simultaneously"""
        tasks = []
        for platform in platforms:
            task = self.publish_video(db, export, platform, user_id, publish_options)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            "total_platforms": len(platforms),
            "successful": len([r for r in results if isinstance(r, dict) and r.get("success")]),
            "failed": len([r for r in results if isinstance(r, dict) and not r.get("success")]),
            "results": results,
        }

    async def get_analytics(self, db: Session, stats_id: str) -> Dict[str, Any]:
        """Get current analytics for a published video"""
        stats = db.query(Stats).filter(Stats.id == stats_id).first()
        if not stats:
            raise ValueError("Stats not found")

        social_account = (
            db.query(SocialAccount)
            .filter(SocialAccount.user_id == stats.user_id, SocialAccount.platform == stats.platform)
            .first()
        )

        if not social_account:
            raise ValueError(f"No {stats.platform} account found")

        # Refresh token if needed
        await self._refresh_token_if_needed(db, social_account)

        # Fetch fresh analytics
        api = self.platform_apis[stats.platform]
        analytics = await api.get_video_analytics(access_token=social_account.access_token, video_id=stats.external_id)

        # Update stats in database
        stats.views = analytics.get("views", 0)
        stats.likes = analytics.get("likes", 0)
        stats.comments = analytics.get("comments", 0)
        stats.shares = analytics.get("shares", 0)
        stats.fetched_at = datetime.utcnow()

        db.commit()

        # Stats are now stored in database only

        return analytics

    async def fetch_and_store_stats(
        self, db: Session, export_id: str, user_id: str, project_id: str, platform: str, external_id: str
    ) -> Stats:
        """Fetch stats from an external platform and store them in DB + stats.json"""
        # Get social account for token access
        social_account = (
            db.query(SocialAccount)
            .filter(SocialAccount.user_id == user_id, SocialAccount.platform == platform)
            .first()
        )

        if not social_account:
            raise ValueError(f"No {platform} account found for user {user_id}")

        # Refresh token if needed
        await self._refresh_token_if_needed(db, social_account)

        # Fetch stats from platform API
        api = self.platform_apis[platform]
        data = await api.get_video_analytics(access_token=social_account.access_token, video_id=external_id)

        # Create stats entry
        stats_id = uuid.uuid4()
        stats = Stats(
            id=stats_id,
            export_id=export_id,
            project_id=project_id,
            user_id=user_id,
            platform=platform,
            external_id=external_id,
            views=data.get("views", 0),
            likes=data.get("likes", 0),
            comments=data.get("comments", 0),
            shares=data.get("shares", 0),
            fetched_at=datetime.utcnow(),
        )
        db.add(stats)
        db.commit()
        db.refresh(stats)

        # Stats are now stored in database only

        return stats

    async def get_connected_accounts(self, db: Session, user_id: str) -> List[Dict[str, Any]]:
        """Get all connected social media accounts for a user"""
        accounts = db.query(SocialAccount).filter(SocialAccount.user_id == user_id).all()
        
        return [
            {
                "id": str(account.id),
                "platform": account.platform,
                "account_name": account.account_name,
                "connected": True,
                "created_at": account.created_at.isoformat(),
            }
            for account in accounts
        ]

    async def disconnect_account(self, db: Session, account_id: str, user_id: str) -> Dict[str, Any]:
        """Disconnect a social media account"""
        account = db.query(SocialAccount).filter(SocialAccount.id == account_id, SocialAccount.user_id == user_id).first()
        
        if not account:
            raise ValueError("Account not found")
        
        db.delete(account)
        db.commit()
        
        return {"success": True, "message": "Account disconnected"}

    async def test_platform_connection(self, platform: str, access_token: str) -> Dict[str, Any]:
        """Test connection to a social media platform without saving"""
        if platform not in ["youtube", "tiktok", "instagram"]:
            raise ValueError("Unsupported platform")
        
        try:
            api = self.platform_apis[platform]
            account_info = await api.get_account_info(access_token)
            return {"success": True, "platform": platform, "account_info": account_info}
        except Exception as e:
            logger.error(f"Failed to test {platform} connection: {e}")
            return {"success": False, "platform": platform, "error": str(e)}

    async def get_supported_platforms(self) -> Dict[str, Any]:
        """Get list of supported social media platforms"""
        return {
            "platforms": [
                {
                    "id": "youtube",
                    "name": "YouTube",
                    "description": "Upload videos to YouTube",
                    "features": ["video_upload", "analytics", "monetization"],
                },
                {
                    "id": "tiktok",
                    "name": "TikTok",
                    "description": "Upload videos to TikTok",
                    "features": ["video_upload", "analytics", "trending"],
                },
                {
                    "id": "instagram",
                    "name": "Instagram",
                    "description": "Upload videos to Instagram",
                    "features": ["video_upload", "analytics", "stories", "reels"],
                },
            ]
        }

    # _update_stats_json method removed - stats are now stored in database only

    async def _refresh_token_if_needed(self, db: Session, social_account: SocialAccount):
        """Refresh OAuth token if it's expired or about to expire"""
        if not social_account.expires_at or social_account.expires_at > datetime.utcnow() + timedelta(minutes=5):
            return

        api = self.platform_apis[social_account.platform]
        new_tokens = await api.refresh_token(social_account.refresh_token)

        social_account.access_token = new_tokens["access_token"]
        if "refresh_token" in new_tokens:
            social_account.refresh_token = new_tokens["refresh_token"]
        social_account.expires_at = datetime.utcnow() + timedelta(seconds=new_tokens.get("expires_in", 3600))

        db.commit()

    async def _get_video_url(self, file_path: str) -> str:
        """Get publicly accessible URL for video file"""
        # This would integrate with your storage service
        # For now, return the file path as URL
        return f"https://storage.example.com/{file_path}"

    async def _schedule_analytics_fetch(self, db: Session, stats: Stats):
        """Schedule periodic analytics fetching"""
        # Wait 1 hour before first fetch
        await asyncio.sleep(3600)

        try:
            analytics = await self.get_analytics(db, stats.id)
            logger.info(f"Fetched analytics for {stats.platform} video {stats.external_id}")
        except Exception as e:
            logger.error(f"Failed to fetch analytics: {e}")


class YouTubeAPI:
    """YouTube Data API v3 integration"""

    def __init__(self):
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.upload_url = "https://www.googleapis.com/upload/youtube/v3/videos"

    async def get_account_info(self, access_token: str) -> Dict[str, Any]:
        """Get YouTube channel information"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/channels",
                params={"part": "snippet", "mine": "true"},
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            data = response.json()

            channel = data["items"][0]
            return {"id": channel["id"], "name": channel["snippet"]["title"]}

    async def upload_video(
        self,
        access_token: str,
        video_url: str,
        title: str,
        description: str,
        tags: List[str],
        privacy: str,
        thumbnail_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload video to YouTube"""
        # This is a simplified version - real implementation would handle file upload
        async with httpx.AsyncClient() as client:
            # First, create the video resource
            video_data = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "categoryId": "10",  # Music category
                },
                "status": {"privacyStatus": privacy},
            }

            response = await client.post(
                f"{self.base_url}/videos",
                params={"part": "snippet,status"},
                headers={"Authorization": f"Bearer {access_token}"},
                json=video_data,
            )
            response.raise_for_status()

            result = response.json()
            return {"id": result["id"], "url": f"https://www.youtube.com/watch?v={result['id']}"}

    async def get_video_analytics(self, access_token: str, video_id: str) -> Dict[str, Any]:
        """Get video analytics from YouTube"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/videos",
                params={"part": "statistics", "id": video_id},
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            data = response.json()

            if not data["items"]:
                return {"views": 0, "likes": 0, "comments": 0, "shares": 0}

            stats = data["items"][0]["statistics"]
            return {
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "shares": 0,  # YouTube doesn't provide share count in basic API
            }

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh YouTube OAuth token"""
        # Implementation would use Google OAuth2 refresh endpoint
        raise NotImplementedError("Token refresh not implemented")


class TikTokAPI:
    """TikTok for Business API integration"""

    def __init__(self):
        self.base_url = "https://business-api.tiktok.com/open_api/v1.3"

    async def get_account_info(self, access_token: str) -> Dict[str, Any]:
        """Get TikTok business account information"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/user/info/", headers={"Access-Token": access_token})
            response.raise_for_status()
            data = response.json()

            return {"id": data["data"]["user"]["open_id"], "name": data["data"]["user"]["display_name"]}

    async def upload_video(
        self,
        access_token: str,
        video_url: str,
        title: str,
        description: str,
        tags: List[str],
        privacy: str,
        thumbnail_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload video to TikTok"""
        # TikTok API requires different approach - this is simplified
        async with httpx.AsyncClient() as client:
            # TikTok uses a multi-step upload process
            # This is a placeholder implementation
            return {
                "id": f"tiktok_{uuid.uuid4().hex[:12]}",
                "url": f"https://www.tiktok.com/@user/video/{uuid.uuid4().hex[:12]}",
            }

    async def get_video_analytics(self, access_token: str, video_id: str) -> Dict[str, Any]:
        """Get video analytics from TikTok"""
        # TikTok analytics API implementation
        return {"views": 0, "likes": 0, "comments": 0, "shares": 0}

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh TikTok OAuth token"""
        raise NotImplementedError("Token refresh not implemented")


class InstagramAPI:
    """Instagram Basic Display API integration"""

    def __init__(self):
        self.base_url = "https://graph.instagram.com"

    async def get_account_info(self, access_token: str) -> Dict[str, Any]:
        """Get Instagram account information"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/me",
                params={"fields": "id,username"},
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            data = response.json()

            return {"id": data["id"], "name": data["username"]}

    async def upload_video(
        self,
        access_token: str,
        video_url: str,
        title: str,
        description: str,
        tags: List[str],
        privacy: str,
        thumbnail_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload video to Instagram"""
        # Instagram API requires different approach for video uploads
        # This is a placeholder implementation
        return {
            "id": f"instagram_{uuid.uuid4().hex[:12]}",
            "url": f"https://www.instagram.com/p/{uuid.uuid4().hex[:12]}/",
        }

    async def get_video_analytics(self, access_token: str, video_id: str) -> Dict[str, Any]:
        """Get video analytics from Instagram"""
        # Instagram analytics API implementation
        return {"views": 0, "likes": 0, "comments": 0, "shares": 0}

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh Instagram OAuth token"""
        raise NotImplementedError("Token refresh not implemented")
