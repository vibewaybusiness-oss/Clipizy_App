# Scripts Directory

This directory contains all startup, deployment, and utility scripts for the Clipizy project.

## Directory Structure

### `/startup/`
Contains scripts for starting and stopping the development environment:
- `stop.sh` - Stops all running services (Docker containers, FastAPI, Next.js, ComfyUI)

### `/backend/`
Contains backend-specific startup and management scripts:
- `start.py` - Main FastAPI server startup script with database health checks
- `init_database.py` - Database initialization script (creates tables and schema)
- `create_admin_user.py` - Script to create admin users manually

### `/deployment/`
Contains scripts for deploying the application:
- `deploy-vercel.sh` - Deploys the API to Vercel (Linux/macOS)
- `deploy-vercel.bat` - Deploys the API to Vercel (Windows)

### `/` (root scripts directory)
Contains general utility scripts:
- `entrypoint.sh` - Docker entrypoint script
- `provision_workspace.sh` - Workspace provisioning script

## Usage

### Starting the Development Environment
From the project root, run:
```bash
./app.sh
```

### Stopping the Development Environment
From the project root, run:
```bash
./scripts/startup/stop.sh
```

### Backend Management
From the project root, run:
```bash
# Initialize database
python scripts/backend/init_database.py

# Create admin user (interactive)
python scripts/backend/create_admin_user.py

# Start backend server (usually done via app.sh)
python scripts/backend/start.py
```

### Deploying to Vercel
From the project root, run:
```bash
# Linux/macOS
./scripts/deployment/deploy-vercel.sh

# Windows
./scripts/deployment/deploy-vercel.bat
```

## Notes

- The main `app.sh` script in the project root is the primary entry point for starting the development environment
- All startup-related scripts have been moved to `/startup/` to keep the project root clean
- Backend management scripts are organized in `/backend/` for easy access
- Deployment scripts are organized in `/deployment/` for easy access
- Core application files (`main.py`, `vercel_main.py`, `db.py`, `config.py`) remain in `/api/` as they are part of the application itself, not startup scripts
