#!/usr/bin/env python3
"""
Diagnostic script to check the synchronization between database and file system
for music-clip projects.
"""

import os
import sys
from pathlib import Path

# Add the api directory to the Python path
api_path = os.path.join(os.path.dirname(__file__), '..', '..', 'api')
sys.path.insert(0, api_path)

try:
    from api.db import get_db, SessionLocal
    from api.models import Project, Track
    from sqlalchemy.orm import Session
except ImportError as e:
    print(f"Error importing API modules: {e}")
    print(f"API path: {api_path}")
    print("Make sure you're running this script from the project root directory")
    sys.exit(1)

def get_storage_projects():
    """Get all projects that exist in the storage system"""
    storage_path = Path("storage/users")
    projects = []
    
    if not storage_path.exists():
        return projects
    
    for user_dir in storage_path.iterdir():
        if user_dir.is_dir():
            user_id = user_dir.name
            music_clip_dir = user_dir / "projects" / "music-clip"
            
            if music_clip_dir.exists():
                for project_dir in music_clip_dir.iterdir():
                    if project_dir.is_dir():
                        # Check if it has music files
                        music_dir = project_dir / "music"
                        music_files = []
                        if music_dir.exists():
                            music_files = [f.name for f in music_dir.iterdir() if f.is_file()]
                        
                        projects.append({
                            'user_id': user_id,
                            'project_id': project_dir.name,
                            'path': str(project_dir),
                            'music_files': music_files,
                            'has_script': (project_dir / "script.json").exists()
                        })
    
    return projects

def get_database_projects():
    """Get all music-clip projects from the database"""
    db = SessionLocal()
    try:
        projects = db.query(Project).filter(Project.type == "music-clip").all()
        
        result = []
        for project in projects:
            # Get tracks for this project
            tracks = db.query(Track).filter(Track.project_id == str(project.id)).all()
            
            result.append({
                'id': str(project.id),
                'name': project.name,
                'user_id': str(project.user_id),
                'created_at': project.created_at.isoformat() if project.created_at else None,
                'tracks': [
                    {
                        'id': str(track.id),
                        'title': track.title,
                        'file_path': track.file_path
                    }
                    for track in tracks
                ]
            })
        
        return result
    finally:
        db.close()

def main():
    print("🔍 Diagnosing storage synchronization...")
    print("=" * 60)
    
    # Get projects from storage
    print("📁 Scanning storage system...")
    storage_projects = get_storage_projects()
    print(f"   Found {len(storage_projects)} projects in storage")
    
    # Get projects from database
    print("🗄️  Scanning database...")
    db_projects = get_database_projects()
    print(f"   Found {len(db_projects)} projects in database")
    
    print()
    
    # Create sets for comparison
    storage_project_ids = {p['project_id'] for p in storage_projects}
    db_project_ids = {p['id'] for p in db_projects}
    
    # Find mismatches
    only_in_storage = storage_project_ids - db_project_ids
    only_in_database = db_project_ids - storage_project_ids
    in_both = storage_project_ids & db_project_ids
    
    print("📊 Synchronization Analysis:")
    print(f"   Projects in both storage and database: {len(in_both)}")
    print(f"   Projects only in storage: {len(only_in_storage)}")
    print(f"   Projects only in database: {len(only_in_database)}")
    print()
    
    if only_in_storage:
        print("🚨 Projects only in storage (orphaned files):")
        for project_id in only_in_storage:
            project = next(p for p in storage_projects if p['project_id'] == project_id)
            print(f"   - {project_id} (User: {project['user_id']}, Files: {len(project['music_files'])})")
        print()
    
    if only_in_database:
        print("🚨 Projects only in database (missing files):")
        for project_id in only_in_database:
            project = next(p for p in db_projects if p['id'] == project_id)
            print(f"   - {project_id} (User: {project['user_id']}, Name: {project['name']})")
            print(f"     Tracks: {len(project['tracks'])}")
            for track in project['tracks']:
                print(f"       - {track['title']} ({track['id']})")
        print()
    
    # Show recent projects
    print("📅 Recent Projects (last 10):")
    recent_projects = sorted(db_projects, key=lambda x: x['created_at'] or '', reverse=True)[:10]
    for project in recent_projects:
        status = "✅" if project['id'] in storage_project_ids else "❌"
        print(f"   {status} {project['id']} - {project['name']} (User: {project['user_id']})")
    
    print()
    print("💡 Recommendations:")
    if only_in_database:
        print("   - Run cleanup_orphaned_projects.py to remove database records for missing files")
    if only_in_storage:
        print("   - Check if these are legitimate files that should be in the database")
    if not only_in_database and not only_in_storage:
        print("   - ✅ Database and storage are in sync!")

if __name__ == "__main__":
    main()
