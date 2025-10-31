#!/usr/bin/env python3
"""
Migration script to fix project directory structure and create missing script.json files
"""
import os
import sys
import json
import uuid
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from api.db import get_db, create_tables
from api.models import Project, Track
from api.services import project_service
from api.config.logging import get_project_logger

logger = get_project_logger()

def migrate_user_projects(user_id: str):
    """Migrate projects for a specific user"""
    logger.info(f"Starting migration for user: {user_id}")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Get all music-clip projects for the user
        projects = db.query(Project).filter(
            Project.user_id == user_id,
            Project.type == "music-clip"
        ).all()
        
        logger.info(f"Found {len(projects)} projects for user {user_id}")
        
        for project in projects:
            project_id = str(project.id)
            logger.info(f"Processing project: {project_id}")
            
            # Check if script.json exists in the correct location
            script_path = f"storage/users/{user_id}/projects/music-clip/{project_id}/script.json"
            
            if not os.path.exists(script_path):
                logger.info(f"Creating missing script.json for project {project_id}")
                
                # Create the directory structure
                os.makedirs(os.path.dirname(script_path), exist_ok=True)
                
                # Get tracks for this project
                tracks = db.query(Track).filter(Track.project_id == project_id).all()
                
                # Create script.json with project data
                script_data = {
                    "steps": {
                        "music": {
                            "tracks": [
                                {
                                    "id": str(track.id),
                                    "file_path": track.file_path,
                                    "ai_generated": track.ai_generated,
                                    "prompt": track.prompt,
                                    "genre": track.genre,
                                    "instrumental": track.instrumental,
                                    "video_description": track.video_description,
                                    "metadata": track.track_metadata or {},
                                    "status": track.status,
                                    "created_at": track.created_at.isoformat() if track.created_at else None
                                }
                                for track in tracks
                            ],
                            "settings": {
                                "videoType": "individual",
                                "budget": [50, 200],
                                "videoStyle": "modern",
                                "animationStyle": "smooth",
                                "createIndividualVideos": True,
                                "createCompilation": False,
                                "useSameVideoForAll": False
                            }
                        },
                        "analysis": {},
                        "visuals": {},
                        "export": {}
                    }
                }
                
                # Save script.json
                with open(script_path, 'w') as f:
                    json.dump(script_data, f, indent=2)
                
                logger.info(f"Created script.json for project {project_id}")
            else:
                logger.info(f"Script.json already exists for project {project_id}")
        
        logger.info(f"Migration completed for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error during migration for user {user_id}: {str(e)}")
        raise
    finally:
        db.close()

def migrate_all_users():
    """Migrate projects for all users"""
    logger.info("Starting migration for all users")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Get all unique user IDs that have music-clip projects
        user_ids = db.query(Project.user_id).filter(
            Project.type == "music-clip"
        ).distinct().all()
        
        logger.info(f"Found {len(user_ids)} users with music-clip projects")
        
        for (user_id,) in user_ids:
            migrate_user_projects(user_id)
        
        logger.info("Migration completed for all users")
        
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        raise
    finally:
        db.close()

def main():
    """Main function"""
    logger.info("Starting project migration script")
    
    # Initialize database
    try:
        create_tables()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return
    
    # Check if specific user ID provided
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
        logger.info(f"Migrating projects for specific user: {user_id}")
        migrate_user_projects(user_id)
    else:
        logger.info("Migrating projects for all users")
        migrate_all_users()
    
    logger.info("Migration script completed")

if __name__ == "__main__":
    main()
