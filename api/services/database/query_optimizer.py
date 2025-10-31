"""
Database Query Optimization Utilities
Provides optimized query patterns to prevent N+1 queries and improve performance
"""

import logging
from typing import List, Optional, Type, Union, Tuple
from sqlalchemy.orm import Session, joinedload, selectinload, contains_eager
from sqlalchemy import and_, or_, desc, asc

from api.models import (
    User, Project, Job, Track, Video, Image, Audio, Export, 
    SocialAccount, CreditsTransaction, Payment, Stats
)

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """Database query optimization utilities"""
    
    @staticmethod
    def get_user_with_projects(db: Session, user_id: str) -> Optional[User]:
        """
        Get user with all their projects in a single query
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User with projects loaded, or None if not found
        """
        return db.query(User)\
            .options(selectinload(User.projects))\
            .filter(User.id == user_id)\
            .first()
    
    @staticmethod
    def get_user_with_all_relations(db: Session, user_id: str) -> Optional[User]:
        """
        Get user with all related data in optimized queries
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User with all relations loaded
        """
        return db.query(User)\
            .options(
                selectinload(User.projects).selectinload(Project.tracks),
                selectinload(User.projects).selectinload(Project.videos),
                selectinload(User.projects).selectinload(Project.images),
                selectinload(User.projects).selectinload(Project.audio),
                selectinload(User.projects).selectinload(Project.exports),
                selectinload(User.jobs),
                selectinload(User.social_accounts),
                selectinload(User.credits_transactions),
                selectinload(User.payments)
            )\
            .filter(User.id == user_id)\
            .first()
    
    @staticmethod
    def get_project_with_all_media(db: Session, project_id: str) -> Optional[Project]:
        """
        Get project with all media files in a single query
        
        Args:
            db: Database session
            project_id: Project ID
            
        Returns:
            Project with all media loaded
        """
        return db.query(Project)\
            .options(
                joinedload(Project.user),
                selectinload(Project.tracks),
                selectinload(Project.videos),
                selectinload(Project.images),
                selectinload(Project.audio),
                selectinload(Project.exports),
                selectinload(Project.jobs)
            )\
            .filter(Project.id == project_id)\
            .first()
    
    @staticmethod
    def get_projects_with_media_by_user(db: Session, user_id: str, project_type: Optional[str] = None) -> List[Project]:
        """
        Get all projects for a user with media files loaded
        
        Args:
            db: Database session
            user_id: User ID
            project_type: Optional project type filter
            
        Returns:
            List of projects with media loaded
        """
        query = db.query(Project)\
            .options(
                selectinload(Project.tracks),
                selectinload(Project.videos),
                selectinload(Project.images),
                selectinload(Project.audio),
                selectinload(Project.exports),
                selectinload(Project.jobs)
            )\
            .filter(Project.user_id == user_id)
        
        if project_type:
            query = query.filter(Project.type == project_type)
        
        return query.all()
    
    @staticmethod
    def get_jobs_with_project_and_user(db: Session, user_id: str) -> List[Job]:
        """
        Get all jobs for a user with project and user data loaded
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of jobs with relations loaded
        """
        return db.query(Job)\
            .options(
                joinedload(Job.project),
                joinedload(Job.user)
            )\
            .filter(Job.user_id == user_id)\
            .order_by(desc(Job.created_at))\
            .all()
    
    @staticmethod
    def get_user_credits_with_transactions(db: Session, user_id: str, limit: int = 10) -> Tuple[Optional[User], List[CreditsTransaction]]:
        """
        Get user with recent credit transactions in optimized queries
        
        Args:
            db: Database session
            user_id: User ID
            limit: Number of recent transactions to load
            
        Returns:
            Tuple of (user, recent_transactions)
        """
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return None, []
        
        # Get recent transactions
        recent_transactions = db.query(CreditsTransaction)\
            .filter(CreditsTransaction.user_id == user_id)\
            .order_by(desc(CreditsTransaction.created_at))\
            .limit(limit)\
            .all()
        
        return user, recent_transactions
    
    @staticmethod
    def get_social_accounts_by_user(db: Session, user_id: str) -> List[SocialAccount]:
        """
        Get social accounts for a user
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of social accounts
        """
        return db.query(SocialAccount)\
            .options(joinedload(SocialAccount.user))\
            .filter(SocialAccount.user_id == user_id)\
            .all()
    
    @staticmethod
    def get_project_media_counts(db: Session, project_id: str) -> dict:
        """
        Get media file counts for a project in a single query
        
        Args:
            db: Database session
            project_id: Project ID
            
        Returns:
            Dictionary with media counts
        """
        from sqlalchemy import func
        
        # Use subqueries to get counts efficiently
        track_count = db.query(func.count(Track.id)).filter(Track.project_id == project_id).scalar() or 0
        video_count = db.query(func.count(Video.id)).filter(Video.project_id == project_id).scalar() or 0
        image_count = db.query(func.count(Image.id)).filter(Image.project_id == project_id).scalar() or 0
        audio_count = db.query(func.count(Audio.id)).filter(Audio.project_id == project_id).scalar() or 0
        export_count = db.query(func.count(Export.id)).filter(Export.project_id == project_id).scalar() or 0
        
        return {
            "tracks": track_count,
            "videos": video_count,
            "images": image_count,
            "audio": audio_count,
            "exports": export_count
        }
    
    @staticmethod
    def get_projects_with_media_counts(db: Session, user_id: str) -> List[dict]:
        """
        Get projects with media counts in optimized queries
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of project data with media counts
        """
        from sqlalchemy import func
        
        # Get projects with media counts using subqueries
        projects = db.query(
            Project,
            func.count(Track.id).label('track_count'),
            func.count(Video.id).label('video_count'),
            func.count(Image.id).label('image_count'),
            func.count(Audio.id).label('audio_count'),
            func.count(Export.id).label('export_count')
        )\
        .outerjoin(Track, Project.id == Track.project_id)\
        .outerjoin(Video, Project.id == Video.project_id)\
        .outerjoin(Image, Project.id == Image.project_id)\
        .outerjoin(Audio, Project.id == Audio.project_id)\
        .outerjoin(Export, Project.id == Export.project_id)\
        .filter(Project.user_id == user_id)\
        .group_by(Project.id)\
        .all()
        
        return [
            {
                "project": project,
                "media_counts": {
                    "tracks": track_count,
                    "videos": video_count,
                    "images": image_count,
                    "audio": audio_count,
                    "exports": export_count
                }
            }
            for project, track_count, video_count, image_count, audio_count, export_count in projects
        ]
    
    @staticmethod
    def bulk_delete_project_media(db: Session, project_id: str) -> dict:
        """
        Efficiently delete all media files for a project
        
        Args:
            db: Database session
            project_id: Project ID
            
        Returns:
            Dictionary with deletion counts
        """
        # Delete in order to respect foreign key constraints
        track_count = db.query(Track).filter(Track.project_id == project_id).delete()
        video_count = db.query(Video).filter(Video.project_id == project_id).delete()
        image_count = db.query(Image).filter(Image.project_id == project_id).delete()
        audio_count = db.query(Audio).filter(Audio.project_id == project_id).delete()
        export_count = db.query(Export).filter(Export.project_id == project_id).delete()
        
        return {
            "tracks_deleted": track_count,
            "videos_deleted": video_count,
            "images_deleted": image_count,
            "audio_deleted": audio_count,
            "exports_deleted": export_count
        }
    
    @staticmethod
    def get_user_stats_summary(db: Session, user_id: str) -> dict:
        """
        Get comprehensive user statistics in optimized queries
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Dictionary with user statistics
        """
        from sqlalchemy import func
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}
        
        # Get counts using subqueries
        project_count = db.query(func.count(Project.id)).filter(Project.user_id == user_id).scalar() or 0
        job_count = db.query(func.count(Job.id)).filter(Job.user_id == user_id).scalar() or 0
        social_account_count = db.query(func.count(SocialAccount.id)).filter(SocialAccount.user_id == user_id).scalar() or 0
        
        return {
            "user": user,
            "project_count": project_count,
            "job_count": job_count,
            "social_account_count": social_account_count,
            "credits_balance": user.credits_balance,
            "total_credits_earned": user.total_credits_earned,
            "total_credits_spent": user.total_credits_spent
        }


class OptimizedQueries:
    """Pre-optimized query patterns for common use cases"""
    
    @staticmethod
    def get_user_dashboard_data(db: Session, user_id: str) -> dict:
        """
        Get all data needed for user dashboard in optimized queries
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Dictionary with all dashboard data
        """
        # Get user with basic info
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}
        
        # Get recent projects with media counts
        recent_projects = QueryOptimizer.get_projects_with_media_counts(db, user_id)[:5]
        
        # Get recent jobs
        recent_jobs = QueryOptimizer.get_jobs_with_project_and_user(db, user_id)[:10]
        
        # Get user stats
        stats = QueryOptimizer.get_user_stats_summary(db, user_id)
        
        return {
            "user": user,
            "recent_projects": recent_projects,
            "recent_jobs": recent_jobs,
            "stats": stats
        }
    
    @staticmethod
    def get_project_detail_data(db: Session, project_id: str) -> dict:
        """
        Get all data needed for project detail page
        
        Args:
            db: Database session
            project_id: Project ID
            
        Returns:
            Dictionary with project detail data
        """
        # Get project with all media
        project = QueryOptimizer.get_project_with_all_media(db, project_id)
        if not project:
            return {}
        
        # Get media counts
        media_counts = QueryOptimizer.get_project_media_counts(db, project_id)
        
        return {
            "project": project,
            "media_counts": media_counts,
            "tracks": project.tracks,
            "videos": project.videos,
            "images": project.images,
            "audio": project.audio,
            "exports": project.exports,
            "jobs": project.jobs
        }
