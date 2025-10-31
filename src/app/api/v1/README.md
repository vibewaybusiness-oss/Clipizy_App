# API v1 Documentation

## Overview

This is the restructured API v1 following RESTful principles and resource-based organization. All routes are now organized by business entities rather than technical implementation.

## Structure

```
/api/v1/
├── auth/                           # Authentication & Authorization
│   ├── login/route.ts
│   ├── register/route.ts
│   ├── refresh/route.ts
│   ├── me/route.ts
│   └── oauth/
│       ├── google/route.ts
│       ├── google/callback/route.ts
│       ├── github/route.ts
│       └── github/callback/route.ts
├── users/                          # User Management
│   ├── [userId]/
│   │   ├── route.ts               # GET, PUT, DELETE user
│   │   ├── profile/route.ts       # User profile operations
│   │   ├── credits/route.ts      # User credits management
│   │   └── preferences/route.ts   # User preferences
│   └── export-data/route.ts       # User data export
├── projects/                       # Music Projects
│   ├── [projectId]/
│   │   ├── route.ts               # GET, PUT, DELETE project
│   │   ├── settings/route.ts      # Project settings
│   │   ├── auto-save/route.ts     # Auto-save functionality
│   │   ├── tracks/
│   │   │   ├── route.ts           # List tracks
│   │   │   ├── upload/route.ts    # Upload single track
│   │   │   ├── upload-batch/route.ts # Batch upload
│   │   │   └── [trackId]/
│   │   │       ├── route.ts       # Track operations
│   │   │       ├── analysis/route.ts # Track analysis
│   │   │       └── metadata/route.ts # Track metadata
│   │   └── videos/
│   │       ├── route.ts           # List videos
│   │       ├── generate/route.ts   # Generate videos
│   │       └── [videoId]/
│   │           ├── route.ts       # Video operations
│   │           └── status/route.ts # Generation status
├── analysis/                       # Analysis Services
│   ├── music/route.ts             # Music analysis
│   ├── comprehensive/route.ts     # Comprehensive analysis
│   ├── batch/route.ts             # Batch analysis
│   └── [analysisId]/
│       ├── route.ts               # Analysis operations
│       └── results/route.ts       # Analysis results
├── generation/                     # Content Generation
│   ├── videos/route.ts            # Video generation
│   ├── audio/route.ts             # Audio generation
│   ├── prompts/route.ts           # Prompt generation
│   ├── scenes/route.ts            # Scene generation
│   └── workflows/
│       ├── route.ts               # List workflows
│       ├── [workflowId]/
│       │   ├── route.ts           # Workflow operations
│       │   ├── generate/route.ts  # Generate with workflow
│       │   └── status/route.ts    # Generation status
│       └── download/route.ts      # Download generated content
├── storage/                        # File Operations
│   ├── upload/route.ts            # File upload
│   ├── download/route.ts          # File download
│   ├── delete/route.ts            # File deletion
│   └── projects/
│       └── [projectId]/
│           └── data/route.ts      # Project data storage
├── exports/                      # Data Export
│   ├── projects/route.ts          # Export projects
│   ├── user-data/route.ts         # Export user data
│   └── [exportId]/
│       ├── route.ts               # Export operations
│       └── download/route.ts      # Download export
├── integrations/                   # External Services
│   ├── ai-providers/
│   │   ├── llm/route.ts           # LLM operations
│   │   ├── generate/route.ts      # AI generation
│   │   └── prompts/route.ts       # Prompt management
│   ├── social-media/
│   │   ├── publish/route.ts       # Publish content
│   │   └── [exportId]/publish/route.ts # Publish specific export
│   ├── email/
│   │   ├── subscribe/route.ts     # Email subscription
│   │   └── unsubscribe/route.ts   # Email unsubscription
│   └── payment/
│       ├── stripe/
│       │   ├── customers/route.ts
│       │   ├── products/route.ts
│       │   ├── prices/route.ts
│       │   └── payment-links/route.ts
│       └── pricing/route.ts       # Pricing configuration
├── admin/                          # Administrative Functions
│   ├── users/
│   │   ├── route.ts               # List users
│   │   └── [userId]/
│   │       ├── route.ts           # User admin operations
│   │       └── credits/route.ts   # Manage user credits
│   ├── analytics/route.ts         # System analytics
│   ├── credits/
│   │   └── add/route.ts           # Add credits to users
│   └── system/route.ts            # System operations
├── content/                        # Content Management
│   ├── blog/
│   │   ├── route.ts               # List blog posts
│   │   └── [slug]/route.ts        # Individual blog post
│   └── placeholder/
│       └── [width]/[height]/route.ts # Placeholder images
├── system/                         # System Operations
│   ├── health/route.ts            # Health check
│   ├── test/route.ts              # Test endpoint
│   └── config/route.ts            # System configuration
├── middleware/                     # Shared Middleware
│   ├── auth.ts                    # Authentication middleware
│   ├── validation.ts              # Request validation
│   ├── rate-limiting.ts           # Rate limiting
│   ├── error-handling.ts          # Error handling
│   ├── logging.ts                 # Request logging
│   └── cors.ts                    # CORS configuration
└── lib/                           # Shared Utilities
    ├── providers/
    │   ├── ai-providers.ts       # AI provider abstraction
    │   ├── storage.ts            # Storage provider
    │   └── email.ts              # Email provider
    ├── validators/
    │   ├── auth.ts               # Auth validation
    │   ├── projects.ts           # Project validation
    │   ├── tracks.ts             # Track validation
    │   └── analysis.ts           # Analysis validation
    ├── transformers/
    │   ├── request.ts            # Request transformation
    │   ├── response.ts            # Response transformation
    │   └── data.ts               # Data transformation
    ├── types/
    │   ├── api.ts                # API types
    │   ├── auth.ts               # Auth types
    │   ├── projects.ts           # Project types
    │   └── analysis.ts           # Analysis types
    └── utils/
        ├── backend.ts             # Backend communication
        ├── file-handling.ts       # File operations
        ├── error-codes.ts         # Error code constants
        └── response-formats.ts    # Standard response formats
```

## Key Features

### 1. Resource-Based Organization
- Routes organized by business entities (users, projects, tracks)
- Clear resource hierarchy with nested resources
- Consistent RESTful patterns

### 2. Shared Middleware
- Centralized authentication with `requireAuth`
- Standardized error handling with `withErrorHandling`
- Consistent validation patterns
- Unified backend communication

### 3. Provider Abstraction
- AI providers abstracted under `/integrations/ai-providers/`
- Payment providers under `/integrations/payment/`
- Social media integrations under `/integrations/social-media/`

### 4. Versioning
- All routes under `/api/v1/`
- Future-proof for breaking changes
- Clear migration path

## Migration from Old Structure

The following routes have been migrated:

| Old Path | New Path | Status |
|----------|----------|--------|
| `/api/auth/*` | `/api/v1/auth/*` | ✅ Migrated |
| `/api/user-management/*` | `/api/v1/users/*` | ✅ Migrated |
| `/api/music-clip/*` | `/api/v1/projects/*` | ✅ Migrated |
| `/api/analysis/*` | `/api/v1/analysis/*` | ✅ Migrated |
| `/api/ai/llm/*` | `/api/v1/integrations/ai-providers/*` | ✅ Migrated |
| `/api/comfyui/*` | `/api/v1/generation/workflows/*` | ✅ Migrated |
| `/api/social-media/*` | `/api/v1/integrations/social-media/*` | ✅ Migrated |
| `/api/mailing/*` | `/api/v1/integrations/email/*` | ✅ Migrated |
| `/api/admin/*` | `/api/v1/admin/*` | ✅ Migrated |

## Usage Examples

### Authentication
```typescript
// Login
POST /api/v1/auth/login
// OAuth
GET /api/v1/auth/oauth/google
// Get current user
GET /api/v1/auth/me
```

### Projects
```typescript
// Get project
GET /api/v1/projects/[projectId]
// Upload track
POST /api/v1/projects/[projectId]/tracks/upload
// Generate video
POST /api/v1/projects/[projectId]/videos/generate
```

### Analysis
```typescript
// Analyze music
POST /api/v1/analysis/music
// Comprehensive analysis
POST /api/v1/analysis/comprehensive
// Track analysis
POST /api/v1/projects/[projectId]/tracks/[trackId]/analysis
```

## Error Handling

All routes use standardized error handling:

```typescript
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request",
    "details": {...}
  }
}
```

## Authentication

Most routes require authentication via Bearer token:

```typescript
Authorization: Bearer <token>
```

## Backend Communication

All routes use the shared `makeBackendRequest` utility for consistent backend communication with proper error handling and timeout management.
