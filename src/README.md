# CLIPIZY FRONTEND STRUCTURE

## OVERVIEW

This document provides a comprehensive overview of the Clipizy frontend codebase structure. The application is built with Next.js 14, React 18, TypeScript, and follows modern architectural patterns for scalability and maintainability.

## DIRECTORY STRUCTURE

```
src/
├── app/                    # Next.js App Router pages and layouts
├── components/             # React components organized by functionality
├── hooks/                  # Custom React hooks for business logic
├── contexts/               # React Context providers for global state
├── utils/                  # Utility functions and helpers
├── types/                  # TypeScript type definitions
├── lib/                    # Library configurations and API clients
├── data/                   # Static data and content
├── examples/               # Code examples and demonstrations
└── __tests__/              # Test files
```

## DETAILED DIRECTORY BREAKDOWN

### APP DIRECTORY (`/app`)

The App Router directory containing all pages, layouts, and API routes.

```
app/
├── layout.tsx              # Root layout with providers
├── page.tsx                # Homepage
├── globals.css             # Global styles and CSS variables
├── actions.ts              # Server actions
├── dashboard/              # Protected dashboard area
│   ├── layout.tsx          # Dashboard layout wrapper
│   ├── page.tsx            # Dashboard overview
│   ├── create/             # Video creation workflows
│   ├── projects/           # Project management
│   ├── analytics/          # Analytics dashboard
│   ├── settings/           # User settings
│   └── credits/            # Credits management
├── auth/                   # Authentication pages
├── pricing/                # Pricing pages
├── admin/                  # Admin panel
├── api/                    # API routes
└── [other-pages]/          # Additional pages
```

**Key Features:**
- Next.js 14 App Router with Server Components
- Protected routes with authentication
- Responsive layouts with conditional rendering
- SEO optimization with metadata

### COMPONENTS DIRECTORY (`/components`)

Organized React components following feature-based architecture.

```
components/
├── ui/                     # shadcn/ui base components
│   ├── button.tsx
│   ├── input.tsx
│   ├── dialog.tsx
│   ├── audio-controls.tsx
│   └── [50+ components]
├── layout/                 # Layout-related components
│   ├── navigation.tsx
│   ├── footer.tsx
│   ├── conditional-layout.tsx
│   ├── protected-route.tsx
│   └── admin-route.tsx
├── common/                 # Shared components
│   ├── clipizy-logo.tsx
│   ├── music-logo.tsx
│   ├── video-theater.tsx
│   ├── user-profile.tsx
│   └── info-popup.tsx
├── forms/                  # Form components
│   ├── BudgetSlider.tsx
│   ├── StepNavigation.tsx
│   └── generators/
├── calendar/               # Calendar components
├── pricing/                # Pricing-related components
├── projects/               # Project management components
├── social-media/           # Social media components
├── seo/                    # SEO components
└── index.ts                # Barrel exports
```

**Architecture Principles:**
- Feature-based organization
- Reusable UI components with shadcn/ui
- Separation of concerns
- Consistent naming conventions (PascalCase)
- Barrel exports for clean imports

### HOOKS DIRECTORY (`/hooks`)

Custom React hooks organized by business domain.

```
hooks/
├── ai/                     # AI-related hooks
│   ├── use-music-analysis.ts
│   ├── use-video-generation.ts
│   ├── use-prompt-generation.ts
│   └── use-producer-music-generation.ts
├── business/               # Business logic hooks
│   ├── use-pricing.ts
│   ├── use-credits.ts
│   ├── use-cost-calculation.ts
│   └── use-form-persistence.ts
├── create/                 # Creation workflow hooks
│   ├── music-clip/
│   └── shared/
├── dashboard/              # Dashboard-specific hooks
├── storage/                # Storage and persistence hooks (legacy + generic)
├── ui/                     # UI interaction hooks
├── users/                  # User management hooks
├── admin/                  # Admin functionality hooks
├── domains/                # Domain-specific hooks
└── utils/                  # Utility hooks
```

**Hook Categories:**
- **Business Logic**: Pricing, credits, cost calculations
- **AI Integration**: Music analysis, video generation, prompt handling
- **UI State**: Form management, loading states, navigation
- **Data Management**: Storage, persistence, API calls
- **Authentication**: User management, admin functions

### CONTEXTS DIRECTORY (`/contexts`)

React Context providers for global state management.

```
contexts/
├── AudioContext.tsx        # Audio playback management
├── auth-context.tsx        # Authentication state
├── loading-context.tsx     # Global loading states
├── pricing-context.tsx     # Pricing and subscription state
└── ThemeContext.tsx        # Theme management (light/dark)
```

**Context Features:**
- **AudioContext**: Manages audio playback, track switching, memory management
- **AuthContext**: User authentication, profile management, OAuth integration
- **LoadingContext**: Global loading states and progress indicators
- **PricingContext**: Subscription management, credit tracking
- **ThemeContext**: Theme switching with system preference detection

### UTILS DIRECTORY (`/utils`)

Utility functions and helper modules.

```
utils/
├── components/             # Component-specific utilities
│   ├── vibewave.utils.ts   # Vibewave component helpers
│   └── waveform.utils.ts   # Waveform visualization utilities
├── music-clip-utils.ts     # Music clip processing utilities
└── memory-management.ts    # Memory management and cleanup
```

**Utility Categories:**
- **Music Processing**: Audio duration, validation, file handling
- **Memory Management**: Blob URL cleanup, event listener management
- **Component Helpers**: Visualization utilities, data formatting
- **Validation**: UUID validation, form validation helpers

### TYPES DIRECTORY (`/types`)

TypeScript type definitions organized by domain.

```
types/
├── domains/                # Domain-specific types
│   ├── admin.ts            # Admin-related types
│   ├── auth.ts             # Authentication types
│   ├── music.ts            # Music and audio types
│   ├── project.ts          # Project management types
│   ├── user.ts             # User profile types
│   └── video.ts            # Video generation types
├── components/             # Component-specific types
│   ├── vibewave.types.ts   # Vibewave component types
│   └── waveform.types.ts   # Waveform types
├── sanitizer.ts            # Input sanitization types
├── settings.ts             # Application settings types
├── optimized-types.ts      # Performance-optimized types
├── global-jsx.d.ts         # Global JSX type extensions
└── index.ts                # Centralized type exports
```

**Type Organization:**
- **Domain Types**: Business logic interfaces
- **Component Types**: React component prop types
- **Utility Types**: Helper and generic types
- **Global Types**: Application-wide type definitions

### LIB DIRECTORY (`/lib`)

Library configurations, API clients, and core utilities.

```
lib/
├── api/                    # API client configurations
├── admin-utils.ts          # Admin utility functions
├── auto-save-service.ts    # Auto-save functionality
├── comfyui-api.ts          # ComfyUI integration
├── config.ts               # Application configuration
├── dashboard-utils.ts      # Dashboard helper functions
├── pricing-utils.ts        # Pricing calculation utilities
├── sanitizer.ts            # Input sanitization
├── utils.ts                # General utility functions
└── index.ts                # Library exports
```

**Library Features:**
- **API Integration**: External service connections
- **Configuration**: Environment and app settings
- **Utilities**: Common helper functions
- **Services**: Business logic services

### DATA DIRECTORY (`/data`)

Static data and content definitions.

```
data/
└── content-calendar.ts     # Content calendar data
```

### EXAMPLES DIRECTORY (`/examples`)

Code examples and integration demonstrations.

```
examples/
└── sanitizer-integration-examples.tsx
```

## ARCHITECTURAL PATTERNS

### 1. FEATURE-BASED ORGANIZATION

Components and hooks are organized by business features rather than technical concerns:
- Music clip creation
- Video generation
- User management
- Pricing and billing

### 2. SEPARATION OF CONCERNS

- **Components**: UI presentation and user interaction
- **Hooks**: Business logic and state management
- **Contexts**: Global state and cross-component communication
- **Utils**: Pure functions and data processing
- **Types**: Type safety and interface definitions

### 3. CUSTOM HOOKS PATTERN

Business logic is extracted into custom hooks for:
- Reusability across components
- Easier testing and debugging
- Cleaner component code
- Better separation of concerns

### 4. CONTEXT PROVIDERS

Global state is managed through React Context:
- Authentication state
- Theme preferences
- Audio playback
- Loading states
- Pricing information

### 5. BARREL EXPORTS

Each directory uses index.ts files for clean imports:
```typescript
// Instead of deep imports
import { Button } from '@/components/ui/button';

// Use barrel exports
import { Button } from '@/components';
```

## NAMING CONVENTIONS

### FILES AND DIRECTORIES
- **Components**: PascalCase (e.g., `BudgetSlider.tsx`)
- **Hooks**: camelCase with `use` prefix (e.g., `usePricing.ts`)
- **Utils**: camelCase with `.utils.ts` suffix (e.g., `music-clip-utils.ts`)
- **Types**: camelCase with `.types.ts` suffix (e.g., `waveform.types.ts`)
- **Directories**: kebab-case (e.g., `music-clip/`)

### COMPONENTS
- **Functional Components**: PascalCase
- **Props Interfaces**: ComponentName + Props (e.g., `ButtonProps`)
- **Event Handlers**: on + Action (e.g., `onClick`, `onSubmit`)

### HOOKS
- **Custom Hooks**: use + Feature (e.g., `usePricing`, `useAudioPlayback`)
- **Hook Returns**: Descriptive object properties
- **Hook Parameters**: Clear, typed interfaces

## PERFORMANCE OPTIMIZATIONS

### 1. MEMORY MANAGEMENT
- Comprehensive blob URL cleanup
- Event listener management
- Timer and animation frame cleanup
- Automatic resource disposal

### 2. CODE SPLITTING
- Dynamic imports for heavy components
- Lazy loading of non-critical features
- Route-based code splitting

### 3. TYPE OPTIMIZATION
- Optimized TypeScript types
- Minimal re-renders through proper typing
- Efficient prop interfaces

## TESTING STRATEGY

### 1. UNIT TESTS
- Component testing with React Testing Library
- Hook testing with custom test utilities
- Utility function testing

### 2. INTEGRATION TESTS
- API integration testing
- Context provider testing
- End-to-end workflow testing

### 3. TEST ORGANIZATION
- Tests co-located with source code
- Shared test utilities
- Mock data and fixtures

## DEVELOPMENT WORKFLOW

### 1. COMPONENT DEVELOPMENT
1. Define TypeScript interfaces
2. Create component with proper props
3. Extract business logic to custom hooks
4. Add comprehensive tests
5. Document usage examples

### 2. FEATURE DEVELOPMENT
1. Plan feature architecture
2. Create necessary types
3. Implement business logic hooks
4. Build UI components
5. Integrate with existing systems
6. Add tests and documentation

### 3. CODE REVIEW CHECKLIST
- [ ] TypeScript types are properly defined
- [ ] Components are properly tested
- [ ] Business logic is in custom hooks
- [ ] Memory management is handled
- [ ] Performance optimizations are applied
- [ ] Documentation is updated

## GETTING STARTED

### 1. SETUP
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

### 2. ADDING NEW COMPONENTS
1. Create component in appropriate directory
2. Define TypeScript interfaces
3. Add to barrel exports
4. Write tests
5. Update documentation

### 3. ADDING NEW HOOKS
1. Create hook in appropriate domain directory
2. Define return type interface
3. Add to hooks index
4. Write comprehensive tests
5. Document usage patterns

## CONCLUSION

## Unified Storage System

### Overview

The frontend includes a unified storage system that supports multiple project types with a single, consistent implementation. This system provides type-safe, consistent APIs for managing different types of projects.

### Storage Hooks

#### Unified Storage Hooks
- `useProjectManagement` - Project management for any project type
- `useDataPersistence` - Data persistence for any project type
- `useUrlStorageIntegration` - URL-storage integration for any project type
- `useProjectFactory` - Factory pattern for creating project-specific handlers

#### Convenience Hooks
- `useMusicClipProject()` - Music clip project handler
- `useVideoEditProject()` - Video editing project handler
- `useAudioEditProject()` - Audio editing project handler
- `useImageEditProject()` - Image editing project handler
- `useCustomProject()` - Custom project handler

### Supported Project Types

```typescript
export type ProjectType = 'music-clip' | 'video-edit' | 'audio-edit' | 'image-edit' | 'custom';

export const PROJECT_CONFIGS = {
  'music-clip': {
    projectType: 'music-clip',
    storagePrefix: 'music-clip',
    allowedFileTypes: ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/ogg'],
    maxFileSize: 50 * 1024 * 1024, // 50MB
    supportedOperations: ['upload', 'generate', 'analyze', 'export']
  },
  'video-edit': {
    projectType: 'video-edit',
    storagePrefix: 'video-edit',
    allowedFileTypes: ['video/mp4', 'video/avi', 'video/mov', 'video/webm'],
    maxFileSize: 500 * 1024 * 1024, // 500MB
    supportedOperations: ['upload', 'edit', 'render', 'export']
  },
  // ... other project types
};
```

### Usage Examples

#### Video Edit Project

```typescript
import { useVideoEditProject } from '@/hooks/storage';

function VideoEditComponent() {
  const videoProject = useVideoEditProject();
  
  const handleCreateProject = async () => {
    const project = await videoProject.createProject({
      name: 'My Video Project',
      type: 'video-edit',
      settings: { resolution: '1080p' }
    });
  };
  
  const handleUploadFile = async (file: File) => {
    const fileId = await videoProject.uploadFile(projectId, file, {
      resolution: '1080p'
    });
  };
}
```

#### Audio Edit Project

```typescript
import { useAudioEditProject } from '@/hooks/storage';

function AudioEditComponent() {
  const audioProject = useAudioEditProject();
  
  const handleCreateProject = async () => {
    const project = await audioProject.createProject({
      name: 'My Audio Project',
      type: 'audio-edit',
      settings: { sampleRate: 44100 }
    });
  };
}
```

#### Generic Project Factory

```typescript
import { useProjectFactory } from '@/hooks/storage';

function CustomProjectComponent() {
  const customProject = useProjectFactory({ projectType: 'custom' });
  
  const handleCreateProject = async () => {
    const project = await customProject.createProject({
      name: 'My Custom Project',
      type: 'custom',
      settings: { customSetting: 'value' }
    });
  };
}
```

### Data Persistence

#### Unified Data Persistence

```typescript
import { useDataPersistence } from '@/hooks/storage';

function ProjectComponent() {
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
  
  // Auto-save on data changes
  useEffect(() => {
    if (hasChanges) {
      dataPersistence.saveDataToBackend();
    }
  }, [hasChanges]);
}
```

### URL Storage Integration

#### Unified URL Storage Integration

```typescript
import { useUrlStorageIntegration } from '@/hooks/storage';

function ProjectPage() {
  const integration = useUrlStorageIntegration({
    currentStep: 1,
    maxReachedStep: 3,
    onStepChange: setCurrentStep,
    projectType: 'video-edit',
    basePath: '/dashboard/create/video-edit',
    projectData: videoProjectData,
    userId: user?.id
  });
  
  // URL and storage are automatically synced
  const { urlProjectId, createProject, loadExistingProject } = integration;
}
```

### API Integration

#### Unified Projects API

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

### Benefits

1. **Type Safety**: Full TypeScript support for all project types
2. **Consistency**: Unified API across all project types
3. **Extensibility**: Easy to add new project types
4. **Performance**: Optimized storage paths and operations per project type
5. **Maintainability**: Single implementation, centralized configuration
6. **Simplicity**: Clean architecture without legacy code

### File Structure

```
src/
├── types/
│   └── projects.ts                           # Core type definitions
├── hooks/storage/
│   ├── use-project-management.ts             # Unified project management
│   ├── use-data-persistence.ts               # Unified data persistence
│   ├── use-project-factory.ts                # Project factory pattern
│   ├── use-url-storage-integration.ts        # Unified URL integration
│   ├── README-GENERIC.md                     # Unified system documentation
│   └── index.ts                              # Updated exports
├── lib/api/
│   ├── projects.ts                           # Unified API service
│   └── auto-save-service.ts                  # Updated auto-save
└── examples/
    └── video-edit-project.tsx                # Usage example
```

This frontend architecture provides a scalable, maintainable, and performant foundation for the Clipizy application. The feature-based organization, custom hooks pattern, comprehensive type system, and unified storage system ensure code quality and developer productivity.

For specific implementation details, refer to the individual component and hook documentation within each directory.