# Unified Storage System

This document describes the unified storage system that supports multiple project types with a single, consistent implementation.

## Overview

The unified storage system provides a single approach to managing different types of projects (music-clip, video-edit, audio-edit, image-edit, custom) with type-specific configurations and operations.

## Architecture


### `useAudioMemoryManagement`
Manages audio memory allocation and cleanup for optimal performance.

### `useDataPersistence`
Handles data persistence operations and state synchronization.

### `useFileUploadHandlers`
Manages file upload operations and progress tracking.

### `useMusicTracks`
Handles music track management and operations.

### `useProjectLoading`
Manages project loading states and operations.

### `useProjectManagement`
Core project management functionality and state.

### `useProjects`
Project listing and basic project operations.

### `useUrlStorageIntegration`
Integrates URL-based storage with application state.


### 1. Type System (`/src/types/projects.ts`)

Defines the core types and configurations for different project types:

```typescript
export type ProjectType = 'music-clip' | 'video-edit' | 'audio-edit' | 'image-edit' | 'custom';

export interface BaseProject {
  id: string;
  name: string;
  description?: string;
  type: ProjectType;
  status: ProjectStatus;
  // ... other fields
}

export const PROJECT_CONFIGS: Record<ProjectType, ProjectStorageConfig> = {
  'music-clip': {
    projectType: 'music-clip',
    storagePrefix: 'music-clip',
    allowedFileTypes: ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/ogg'],
    maxFileSize: 50 * 1024 * 1024, // 50MB
    supportedOperations: ['upload', 'generate', 'analyze', 'export']
  },
  // ... other project types
};
```

### 2. Unified Hooks

#### `useProjectManagement`
Manages project lifecycle for any project type:

```typescript
const projectManagement = useProjectManagement({
  projectType: 'video-edit',
  storagePrefix: 'video-edit'
});

// Create a new project
const projectId = await projectManagement.actions.createProject({
  name: 'My Video Project',
  description: 'A video editing project',
  type: 'video-edit'
});
```

#### `useDataPersistence`
Handles data persistence for any project type:

```typescript
const dataPersistence = useDataPersistence({
  projectId: 'project-123',
  userId: 'user-456',
  projectType: 'video-edit',
  projectData: {
    settings: { resolution: '1080p' },
    tracks: [],
    analysis: null,
    media: [],
    metadata: {}
  }
});

// Save data to backend
await dataPersistence.saveDataToBackend();
```

#### `useProjectFactory`
Factory pattern for creating project-specific handlers:

```typescript
// For video editing projects
const videoProject = useVideoEditProject();

// For audio editing projects  
const audioProject = useAudioEditProject();

// Generic factory
const customProject = useProjectFactory({ projectType: 'custom' });
```

#### `useUrlStorageIntegration`
Integrates URL management with storage for any project type:

```typescript
const integration = useUrlStorageIntegration({
  currentStep: 1,
  maxReachedStep: 3,
  onStepChange: setCurrentStep,
  projectType: 'video-edit',
  basePath: '/dashboard/create/video-edit',
  projectData: videoProjectData,
  userId: user?.id
});
```

### 3. API Services

#### Unified Projects API (`/src/lib/api/projects.ts`)

Provides a unified API service for all project types:

```typescript
import { projectsAPI } from '@/lib/api/projects';

// Create project
const project = await projectsAPI.createProject({
  name: 'My Project',
  type: 'video-edit',
  description: 'A video editing project'
});

// Upload file
const fileId = await projectsAPI.uploadProjectFile(
  projectId, 
  file, 
  { metadata: 'additional info' }
);

// Save project data
await projectsAPI.saveProjectData(projectId, {
  settings: { resolution: '1080p' },
  tracks: [],
  analysis: null,
  media: [],
  metadata: {}
});
```

### 4. Backend Services

#### Unified Storage Service (`/api/services/storage/storage.py`)

Handles storage operations for multiple project types:

```python
from api.services.storage import storage_service

# Upload file for any project type
file_info = await storage_service.upload_project_file(
    user_id=user_id,
    project_id=project_id,
    project_type='video-edit',
    file=uploaded_file,
    metadata={'resolution': '1080p'}
)

# Save project data
await storage_service.save_project_data(
    user_id=user_id,
    project_id=project_id,
    project_type='video-edit',
    data=project_data
)
```

#### Unified Storage Router (`/api/routers/storage/storage.py`)

Provides HTTP endpoints for all project types:

```python
# Create project
POST /api/storage/projects
{
  "name": "My Video Project",
  "type": "video-edit",
  "description": "A video editing project"
}

# Upload file
POST /api/storage/projects/{project_id}/files/upload

# Save project data
POST /api/storage/projects/{project_id}/data
```

## Usage Examples

### Creating a New Project Type

1. **Add to type definitions**:
```typescript
// In /src/types/projects.ts
export type ProjectType = 'music-clip' | 'video-edit' | 'audio-edit' | 'image-edit' | 'custom' | 'new-type';

export const PROJECT_CONFIGS = {
  // ... existing configs
  'new-type': {
    projectType: 'new-type',
    storagePrefix: 'new-type',
    allowedFileTypes: ['application/pdf', 'text/plain'],
    maxFileSize: 10 * 1024 * 1024, // 10MB
    supportedOperations: ['upload', 'process', 'export']
  }
};
```

2. **Create convenience hook**:
```typescript
// In /src/hooks/storage/use-project-factory.ts
export function useNewTypeProject() {
  return useProjectFactory({ projectType: 'new-type' });
}
```

3. **Use in components**:
```typescript
const newTypeProject = useNewTypeProject();

const handleCreateProject = async () => {
  const project = await newTypeProject.createProject({
    name: 'My New Type Project',
    type: 'new-type',
    description: 'A new type of project'
  });
};
```

### Migrating from Legacy System

All project types use the same unified system:

```typescript
// Unified approach for all project types
import { useProjectManagement } from '@/hooks/storage';
import { useMusicClipProject } from '@/hooks/storage';
import { useVideoEditProject } from '@/hooks/storage';

// All use the same underlying unified system
```

## Benefits

1. **Type Safety**: Full TypeScript support for all project types
2. **Consistency**: Unified API across all project types
3. **Extensibility**: Easy to add new project types
4. **Performance**: Optimized storage paths and operations per project type
5. **Maintainability**: Single implementation, centralized configuration
6. **Simplicity**: Clean architecture without legacy code

## File Structure

```
src/
├── types/
│   └── projects.ts                    # Core type definitions
├── hooks/storage/
│   ├── use-project-management.ts      # Unified project management
│   ├── use-data-persistence.ts        # Unified data persistence
│   ├── use-project-factory.ts         # Project factory pattern
│   ├── use-url-storage-integration.ts # Unified URL integration
│   └── index.ts                       # Updated exports
├── lib/api/
│   ├── projects.ts                    # Unified API service
│   └── auto-save-service.ts           # Updated auto-save
└── ...

api/
├── services/storage/
│   └── storage.py                     # Unified storage service
└── routers/storage/
    └── storage.py                     # Unified storage router
```

## Usage

All project types use the same unified system:

```typescript
// For any project type
import { useProjectManagement } from '@/hooks/storage';
import { useVideoEditProject } from '@/hooks/storage';
import { useMusicClipProject } from '@/hooks/storage';

// All use the same underlying unified system
```

## Configuration

Each project type can be configured with:

- **Storage Prefix**: Used in S3 paths and localStorage keys
- **Allowed File Types**: MIME types allowed for uploads
- **Max File Size**: Maximum file size for uploads
- **Supported Operations**: List of operations available for the project type

This allows for fine-tuned control over each project type's behavior while maintaining a unified interface.
