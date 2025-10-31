#!/usr/bin/env python3
"""
Simple script to check what projects exist in the storage system
without requiring database access.
"""

import os
from pathlib import Path

def get_storage_projects():
    """Get all projects that exist in the storage system"""
    storage_path = Path("storage/users")
    projects = []
    
    if not storage_path.exists():
        print(f"❌ Storage path does not exist: {storage_path}")
        return projects
    
    print(f"📁 Scanning storage path: {storage_path}")
    
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
                        
                        # Check if it has script.json
                        script_file = project_dir / "script.json"
                        has_script = script_file.exists()
                        
                        projects.append({
                            'user_id': user_id,
                            'project_id': project_dir.name,
                            'path': str(project_dir),
                            'music_files': music_files,
                            'has_script': has_script,
                            'music_count': len(music_files)
                        })
    
    return projects

def main():
    print("🔍 Simple Storage System Check")
    print("=" * 50)
    
    # Get projects from storage
    storage_projects = get_storage_projects()
    
    if not storage_projects:
        print("❌ No projects found in storage system")
        return
    
    print(f"📊 Found {len(storage_projects)} projects in storage")
    print()
    
    # Group by user
    users = {}
    for project in storage_projects:
        user_id = project['user_id']
        if user_id not in users:
            users[user_id] = []
        users[user_id].append(project)
    
    print("👥 Projects by User:")
    print("-" * 30)
    
    for user_id, user_projects in users.items():
        print(f"User: {user_id}")
        print(f"  Projects: {len(user_projects)}")
        
        for project in user_projects:
            status = "✅" if project['has_script'] else "⚠️"
            print(f"  {status} {project['project_id']}")
            print(f"     Music files: {project['music_count']}")
            if project['music_files']:
                for file in project['music_files'][:3]:  # Show first 3 files
                    print(f"       - {file}")
                if len(project['music_files']) > 3:
                    print(f"       ... and {len(project['music_files']) - 3} more")
            print()
    
    # Show recent projects (by directory modification time)
    print("📅 Recent Projects (by directory modification time):")
    print("-" * 50)
    
    recent_projects = sorted(storage_projects, 
                           key=lambda x: Path(x['path']).stat().st_mtime, 
                           reverse=True)[:10]
    
    for project in recent_projects:
        mod_time = Path(project['path']).stat().st_mtime
        import datetime
        mod_date = datetime.datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
        status = "✅" if project['has_script'] else "⚠️"
        print(f"  {status} {project['project_id']} - {mod_date}")
        print(f"     User: {project['user_id']}, Files: {project['music_count']}")
    
    print()
    print("💡 Notes:")
    print("   ✅ = Has script.json file")
    print("   ⚠️  = Missing script.json file")
    print("   This check only shows what exists in the file system")
    print("   Use the full diagnostic script to compare with database")

if __name__ == "__main__":
    main()
