# Projects Page Data Retrieval Improvements

## Overview
Enhanced the projects page to properly retrieve and display data from PostgreSQL database and S3 storage, including project thumbnails, export previews, and media counts.

## Changes Made

### Backend Changes

#### 1. Enhanced Projects List Endpoint (`api/routers/storage/backend_storage.py`)
- **Endpoint**: `GET /api/storage/projects`
- **Improvements**:
  - Added `user_id` to project response
  - Retrieves latest export file with presigned S3 URL (`preview_url`)
  - Retrieves project thumbnail with presigned S3 URL (`thumbnail_url`)
  - Includes media counts (tracks, videos, images)
  - Generates presigned URLs with 1-hour expiration for all media files

**New Response Format**:
```json
{
  "success": true,
  "data": {
    "projects": [
      {
        "id": "project-uuid",
        "name": "Project Name",
        "type": "music-clip",
        "description": "Project description",
        "status": "completed",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
        "user_id": "user-uuid",
        "preview_url": "https://s3-presigned-url/export.mp4",
        "thumbnail_url": "https://s3-presigned-url/thumbnail.jpg",
        "export_id": "export-uuid",
        "media_counts": {
          "tracks": 2,
          "videos": 1,
          "images": 3
        }
      }
    ],
    "count": 1
  },
  "message": "Projects retrieved successfully"
}
```

### Frontend Changes

#### 2. Updated Type Definitions

**File**: `src/types/projects.ts`
- Added optional fields to `BaseProject` interface:
  - `preview_url?: string` - Presigned URL to project export video
  - `thumbnail_url?: string` - Presigned URL to project thumbnail image
  - `export_id?: string` - ID of the latest export
  - `media_counts?: { tracks, videos, images }` - Count of media files

**File**: `src/lib/dashboard-utils.ts`
- Updated `Project` interface with same fields for consistency

#### 3. Enhanced Project Card Component

**File**: `src/components/projects/project-card.tsx`
- **Visual Improvements**:
  - Displays thumbnail/preview image at the top of the card (if available)
  - Shows "Completed" badge overlay on thumbnail for completed projects
  - Displays media counts with icons at the bottom of the card
  - Graceful fallback if image fails to load

## Database Integration

### PostgreSQL Tables Used
- **projects**: Main project metadata
- **exports**: Final rendered videos/outputs
- **images**: Project thumbnails and cover images (filtered by `type='thumbnail'`)
- **tracks**: Audio tracks associated with project
- **videos**: Video files in project
- **audio**: Additional audio files

### S3 Integration
- All file URLs are generated using presigned URLs with 1-hour expiration
- Uses `backend_storage_service.get_presigned_url()` method
- Proper error handling if S3 URLs cannot be generated

## Data Flow

```
1. User opens /dashboard/projects
   ↓
2. useProjects hook calls projectsAPI.getProjects(userId)
   ↓
3. API client sends GET /api/storage/projects with auth token
   ↓
4. Backend:
   - Queries projects from PostgreSQL
   - For each project:
     * Finds latest export → generates S3 URL
     * Finds thumbnail → generates S3 URL
     * Counts media files
   - Returns enriched project list
   ↓
5. Frontend:
   - Displays projects in grid/list view
   - Shows thumbnails/previews
   - Shows media counts
   - Handles filtering and search
```

## Testing Instructions

### 1. Backend Testing

Start the backend server:
```bash
cd /root/clipizy
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Test the endpoint (requires authentication):
```bash
# Get auth token first (replace with your credentials)
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"your-email@example.com","password":"your-password"}' \
  | jq -r '.access_token')

# Test projects endpoint
curl -X GET http://localhost:8000/api/storage/projects \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

### 2. Frontend Testing

Start the frontend server:
```bash
cd /root/clipizy
npm run dev
```

Navigate to: `http://localhost:3000/dashboard/projects`

**Expected Behavior**:
- Projects load from database
- If projects have exports, preview images are displayed
- If projects have thumbnails, they are displayed
- Media counts are shown at the bottom of cards
- S3 URLs are properly generated and images load
- Filtering and search work correctly

### 3. Data Verification

Check if projects have associated media:
```sql
-- Check projects
SELECT id, name, type, status, created_at FROM projects ORDER BY created_at DESC LIMIT 10;

-- Check exports for a project
SELECT id, project_id, file_path, format, created_at FROM exports WHERE project_id = 'your-project-id';

-- Check thumbnails for a project
SELECT id, project_id, file_path, type, created_at FROM images WHERE project_id = 'your-project-id' AND type = 'thumbnail';

-- Check media counts
SELECT 
  p.id, 
  p.name,
  COUNT(DISTINCT t.id) as tracks,
  COUNT(DISTINCT v.id) as videos,
  COUNT(DISTINCT i.id) as images
FROM projects p
LEFT JOIN tracks t ON t.project_id = p.id
LEFT JOIN videos v ON v.project_id = p.id
LEFT JOIN images i ON i.project_id = p.id
GROUP BY p.id, p.name;
```

## Error Handling

### Backend
- Graceful handling of missing exports/thumbnails
- Logs warnings if S3 URL generation fails
- Returns projects even if media URLs cannot be generated
- Proper error responses with status codes

### Frontend
- Falls back to icon if no thumbnail available
- Hides image if S3 URL fails to load
- Shows empty state if no projects exist
- Displays error message if API call fails

## Performance Considerations

1. **Database Queries**: 
   - Uses efficient queries with proper indexing
   - Orders by `updated_at DESC` for most recent first

2. **S3 Presigned URLs**:
   - Generated on-demand for each request
   - 1-hour expiration (adjustable via `expiration` parameter)
   - Cached by browser during expiration period

3. **Frontend**:
   - Projects data cached in React state
   - Lazy image loading with error handling
   - Optimized re-renders with useMemo and useCallback

## Future Enhancements

1. **Pagination**: Add pagination for large project lists
2. **Lazy Loading**: Load thumbnails only when in viewport
3. **URL Caching**: Cache presigned URLs in backend for shorter durations
4. **Video Previews**: Add hover-to-play preview for export videos
5. **Bulk Operations**: Add support for bulk export/download
6. **Advanced Filtering**: Filter by date ranges, media types
7. **Sorting Options**: Sort by name, date, status, type

## Troubleshooting

### Projects Not Loading
- Check authentication token in localStorage
- Verify backend is running on port 8000
- Check browser console for API errors
- Verify database connection in backend logs

### Images Not Displaying
- Check S3 bucket permissions
- Verify file_path in database matches S3 keys
- Check browser console for CORS errors
- Verify S3 credentials in backend settings

### Slow Loading
- Check database query performance
- Verify S3 connection speed
- Consider adding pagination
- Check network tab for slow requests

## Files Modified

### Backend
- `api/routers/storage/backend_storage.py` - Enhanced list_projects endpoint

### Frontend
- `src/types/projects.ts` - Added new fields to BaseProject
- `src/lib/dashboard-utils.ts` - Updated Project interface
- `src/components/projects/project-card.tsx` - Added thumbnail display and media counts

## Dependencies
- No new dependencies added
- Uses existing S3 and PostgreSQL infrastructure
- Compatible with current authentication system

