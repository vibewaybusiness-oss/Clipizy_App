# Projects Page

This page displays and manages user projects in the clipizy application.

## Features

- **Project Listing**: Display all user projects in grid or list view
- **Filtering**: Filter projects by type (music-clip, video-clip, short-clip)
- **Search**: Search projects by name or description
- **Project Actions**: View, edit, and delete projects
- **Status Indicators**: Visual status badges for project states
- **Responsive Design**: Works on desktop and mobile devices

## Project Types

- **Music Clips**: Audio-focused projects
- **Video Clips**: Video content projects  
- **Short Clips**: Short-form content projects

## Project Statuses

- **Draft**: Project created but not started
- **Created**: Project initialized
- **Uploading**: Files being uploaded
- **Analyzing**: Content being analyzed
- **Queued**: Waiting for processing
- **Processing**: Currently being processed
- **Completed**: Successfully finished
- **Failed**: Processing failed
- **Cancelled**: User cancelled

## Components

### ProjectsPage
Main page component that handles:
- Data fetching using `useProjects` hook
- Filtering and search logic
- View mode switching (grid/list)
- Error handling and loading states

### ProjectCard
Reusable component for displaying individual projects:
- Supports both grid and list view modes
- Displays project information and status
- Provides action buttons (play, edit, delete)
- Handles project interactions

### API Integration
- **ProjectsAPI**: Service class for all project operations
- **useProjects**: Custom hook for state management
- **API Routes**: Next.js API routes that proxy to backend

## API Endcredits

- `GET /api/projects` - List all projects
- `GET /api/projects/[id]` - Get specific project
- `POST /api/projects` - Create new project
- `PUT /api/projects/[id]` - Update project
- `DELETE /api/projects/[id]` - Delete project

## Development

The page uses mock data in development mode. Set `NODE_ENV=production` to use real backend API.

## Usage

```tsx
import { ProjectsPage } from '@/app/dashboard/projects/page';

// The page is automatically available at /dashboard/projects
```

## Future Enhancements

- Project creation modal
- Bulk operations (select multiple projects)
- Project templates
- Advanced filtering options
- Project sharing
- Export functionality
