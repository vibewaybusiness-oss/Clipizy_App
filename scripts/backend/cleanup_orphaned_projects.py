#!/usr/bin/env python3
"""
Cleanup script to identify and optionally remove orphaned projects
that exist in the database but not in the file system.
"""

import os
import sys
import argparse
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

def check_project_exists_in_storage(project_id: str, user_id: str) -> bool:
    """Check if a project directory exists in the storage system"""
    project_path = Path(f"storage/users/{user_id}/projects/music-clip/{project_id}")
    return project_path.exists()

def check_track_exists_in_storage(track_file_path: str) -> bool:
    """Check if a track file exists in the storage system"""
    if track_file_path.startswith("file://"):
        # Convert file:// path to actual file path
        local_path = track_file_path.replace("file://", "")
        full_path = Path("storage") / local_path
        return full_path.exists()
    elif track_file_path.startswith("http://") or track_file_path.startswith("https://"):
        # For HTTP URLs, we can't easily check existence without downloading
        # Return True to avoid false positives
        return True
    else:
        # Assume it's a relative path
        full_path = Path("storage") / track_file_path
        return full_path.exists()

def find_orphaned_projects(dry_run: bool = True) -> dict:
    """Find projects that exist in database but not in storage"""
    db = SessionLocal()
    try:
        # Get all music-clip projects
        projects = db.query(Project).filter(Project.type == "music-clip").all()
        
        orphaned_projects = []
        valid_projects = []
        
        for project in projects:
            user_id = str(project.user_id)
            project_id = str(project.id)
            
            exists_in_storage = check_project_exists_in_storage(project_id, user_id)
            
            if exists_in_storage:
                valid_projects.append({
                    'id': project_id,
                    'name': project.name,
                    'user_id': user_id,
                    'created_at': project.created_at.isoformat() if project.created_at else None
                })
            else:
                # Get tracks for this project
                tracks = db.query(Track).filter(Track.project_id == project_id).all()
                track_info = []
                
                for track in tracks:
                    track_exists = check_track_exists_in_storage(track.file_path)
                    track_info.append({
                        'id': str(track.id),
                        'title': track.title,
                        'file_path': track.file_path,
                        'exists_in_storage': track_exists
                    })
                
                orphaned_projects.append({
                    'id': project_id,
                    'name': project.name,
                    'user_id': user_id,
                    'created_at': project.created_at.isoformat() if project.created_at else None,
                    'tracks': track_info
                })
        
        return {
            'orphaned_projects': orphaned_projects,
            'valid_projects': valid_projects,
            'total_projects': len(projects),
            'orphaned_count': len(orphaned_projects),
            'valid_count': len(valid_projects)
        }
        
    finally:
        db.close()

def remove_orphaned_projects(orphaned_projects: list, dry_run: bool = True) -> dict:
    """Remove orphaned projects from the database"""
    if dry_run:
        return {
            'message': 'DRY RUN - No projects were actually deleted',
            'would_delete': len(orphaned_projects),
            'projects': [p['id'] for p in orphaned_projects]
        }
    
    db = SessionLocal()
    try:
        deleted_count = 0
        deleted_projects = []
        
        for project_info in orphaned_projects:
            project_id = project_info['id']
            
            # Delete associated tracks first
            tracks_deleted = db.query(Track).filter(Track.project_id == project_id).delete()
            
            # Delete the project
            project = db.query(Project).filter(Project.id == project_id).first()
            if project:
                db.delete(project)
                deleted_count += 1
                deleted_projects.append(project_id)
        
        db.commit()
        
        return {
            'message': f'Successfully deleted {deleted_count} orphaned projects',
            'deleted_count': deleted_count,
            'deleted_projects': deleted_projects
        }
        
    except Exception as e:
        db.rollback()
        return {
            'error': f'Failed to delete orphaned projects: {str(e)}',
            'deleted_count': 0
        }
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description='Cleanup orphaned music-clip projects')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Only show what would be deleted (default: True)')
    parser.add_argument('--delete', action='store_true',
                       help='Actually delete orphaned projects (use with caution)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed information')
    
    args = parser.parse_args()
    
    if args.delete:
        args.dry_run = False
    
    print("🔍 Scanning for orphaned music-clip projects...")
    print("=" * 60)
    
    # Find orphaned projects
    result = find_orphaned_projects(dry_run=args.dry_run)
    
    print(f"📊 Summary:")
    print(f"   Total projects in database: {result['total_projects']}")
    print(f"   Valid projects (exist in storage): {result['valid_count']}")
    print(f"   Orphaned projects (missing from storage): {result['orphaned_count']}")
    print()
    
    if result['orphaned_projects']:
        print("🚨 Orphaned Projects Found:")
        print("-" * 40)
        
        for project in result['orphaned_projects']:
            print(f"Project ID: {project['id']}")
            print(f"Name: {project['name']}")
            print(f"User ID: {project['user_id']}")
            print(f"Created: {project['created_at']}")
            print(f"Tracks: {len(project['tracks'])}")
            
            if args.verbose:
                for track in project['tracks']:
                    status = "✅" if track['exists_in_storage'] else "❌"
                    print(f"  {status} {track['title']} ({track['id']})")
                    if not track['exists_in_storage']:
                        print(f"     Path: {track['file_path']}")
            
            print()
        
        # Ask for confirmation if not dry run
        if not args.dry_run:
            response = input(f"⚠️  Are you sure you want to delete {len(result['orphaned_projects'])} orphaned projects? (yes/no): ")
            if response.lower() != 'yes':
                print("❌ Operation cancelled")
                return
        
        # Remove orphaned projects
        delete_result = remove_orphaned_projects(result['orphaned_projects'], dry_run=args.dry_run)
        
        if 'error' in delete_result:
            print(f"❌ {delete_result['error']}")
        else:
            print(f"✅ {delete_result['message']}")
            if not args.dry_run:
                print(f"   Deleted projects: {delete_result['deleted_projects']}")
    else:
        print("✅ No orphaned projects found!")
    
    print()
    print("💡 Tips:")
    print("   - Use --verbose to see detailed track information")
    print("   - Use --delete to actually remove orphaned projects")
    print("   - Always backup your database before running with --delete")

if __name__ == "__main__":
    main()
