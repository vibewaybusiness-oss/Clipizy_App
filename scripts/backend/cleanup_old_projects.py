#!/usr/bin/env python3
"""
Cleanup script to remove old project directory structure
"""
import os
import sys
import shutil

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from api.config.logging import get_project_logger

logger = get_project_logger()

def cleanup_old_project_structure(user_id: str):
    """Remove old project directory structure for a user"""
    logger.info(f"Cleaning up old project structure for user: {user_id}")
    
    # Old structure: users/{user_id}/music-clip/projects/
    old_path = f"users/{user_id}/music-clip/projects"
    
    if os.path.exists(old_path):
        logger.info(f"Found old project structure at: {old_path}")
        
        # List all projects in old structure
        old_projects = os.listdir(old_path)
        logger.info(f"Found {len(old_projects)} projects in old structure")
        
        # Check if these projects exist in the new structure
        new_path = f"storage/users/{user_id}/projects/music-clip"
        if os.path.exists(new_path):
            new_projects = os.listdir(new_path)
            logger.info(f"Found {len(new_projects)} projects in new structure")
            
            # Only remove old projects that exist in new structure
            for project_id in old_projects:
                if project_id in new_projects:
                    old_project_path = os.path.join(old_path, project_id)
                    logger.info(f"Removing old project structure: {old_project_path}")
                    shutil.rmtree(old_project_path)
                else:
                    logger.warning(f"Project {project_id} not found in new structure, keeping old structure")
        else:
            logger.warning(f"New project structure not found at: {new_path}")
    else:
        logger.info(f"No old project structure found at: {old_path}")

def cleanup_all_users():
    """Cleanup old project structure for all users"""
    logger.info("Cleaning up old project structure for all users")
    
    users_dir = "users"
    if not os.path.exists(users_dir):
        logger.info("No users directory found")
        return
    
    user_dirs = [d for d in os.listdir(users_dir) if os.path.isdir(os.path.join(users_dir, d))]
    logger.info(f"Found {len(user_dirs)} user directories")
    
    for user_id in user_dirs:
        cleanup_old_project_structure(user_id)

def main():
    """Main function"""
    logger.info("Starting cleanup script")
    
    # Check if specific user ID provided
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
        logger.info(f"Cleaning up for specific user: {user_id}")
        cleanup_old_project_structure(user_id)
    else:
        logger.info("Cleaning up for all users")
        cleanup_all_users()
    
    logger.info("Cleanup script completed")

if __name__ == "__main__":
    main()
