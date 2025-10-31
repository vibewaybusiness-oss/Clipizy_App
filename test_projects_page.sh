#!/bin/bash

echo "================================"
echo "Projects Page Testing Script"
echo "================================"
echo ""

echo "1. Checking Backend Server..."
BACKEND_PID=$(ps aux | grep "[u]vicorn api.main:app" | awk '{print $2}')
if [ -z "$BACKEND_PID" ]; then
    echo "❌ Backend server is NOT running"
    echo "   Start it with: python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
else
    echo "✅ Backend server is running (PID: $BACKEND_PID)"
fi
echo ""

echo "2. Checking Frontend Server..."
FRONTEND_PID=$(ps aux | grep "[n]ext-server" | awk '{print $2}')
if [ -z "$FRONTEND_PID" ]; then
    echo "❌ Frontend server is NOT running"
    echo "   Start it with: npm run dev"
else
    echo "✅ Frontend server is running (PID: $FRONTEND_PID)"
fi
echo ""

echo "3. Checking Database Connection..."
if command -v psql &> /dev/null; then
    DB_CHECK=$(psql postgresql://postgres:postgres@localhost:5432/clipizy -c "SELECT 1" 2>&1)
    if [ $? -eq 0 ]; then
        echo "✅ Database connection successful"
    else
        echo "❌ Database connection failed"
        echo "   Check your PostgreSQL connection"
    fi
else
    echo "⚠️  psql not found, skipping database check"
fi
echo ""

echo "4. Checking Projects in Database..."
if command -v psql &> /dev/null; then
    echo "   Querying projects..."
    psql postgresql://postgres:postgres@localhost:5432/clipizy -c "
    SELECT 
        COUNT(*) as total_projects,
        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
        COUNT(CASE WHEN status = 'draft' THEN 1 END) as draft,
        COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing
    FROM projects;" 2>/dev/null || echo "   ⚠️  Could not query database"
else
    echo "   ⚠️  psql not found, skipping database query"
fi
echo ""

echo "5. Checking S3 Configuration..."
if [ -f "api/config/settings.py" ]; then
    echo "   ✅ Settings file exists"
    grep -q "s3_bucket" api/config/settings.py && echo "   ✅ S3 bucket configured" || echo "   ⚠️  S3 bucket not configured"
else
    echo "   ⚠️  Settings file not found"
fi
echo ""

echo "6. Testing Backend Endpoint (requires authentication)..."
echo "   Endpoint: GET /api/storage/projects"
if [ ! -z "$BACKEND_PID" ]; then
    # Try to get health check first
    HEALTH_CHECK=$(curl -s http://localhost:8000/health 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "   ✅ Backend is responding"
        echo "   ℹ️  To test with authentication:"
        echo "      1. Login at http://localhost:3000/auth/login"
        echo "      2. Copy the access_token from localStorage"
        echo "      3. Run: curl -H 'Authorization: Bearer YOUR_TOKEN' http://localhost:8000/api/storage/projects"
    else
        echo "   ❌ Backend is not responding"
    fi
else
    echo "   ⚠️  Backend not running"
fi
echo ""

echo "7. Quick File Check..."
echo "   Checking modified files..."
[ -f "api/routers/storage/backend_storage.py" ] && echo "   ✅ backend_storage.py exists" || echo "   ❌ backend_storage.py missing"
[ -f "src/types/projects.ts" ] && echo "   ✅ projects.ts exists" || echo "   ❌ projects.ts missing"
[ -f "src/components/projects/project-card.tsx" ] && echo "   ✅ project-card.tsx exists" || echo "   ❌ project-card.tsx missing"
[ -f "src/lib/dashboard-utils.ts" ] && echo "   ✅ dashboard-utils.ts exists" || echo "   ❌ dashboard-utils.ts missing"
echo ""

echo "================================"
echo "Manual Testing Steps:"
echo "================================"
echo "1. Ensure backend is running: python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
echo "2. Ensure frontend is running: npm run dev"
echo "3. Navigate to: http://localhost:3000/auth/login"
echo "4. Login with your credentials"
echo "5. Navigate to: http://localhost:3000/dashboard/projects"
echo "6. Verify:"
echo "   - Projects list loads from database"
echo "   - Project cards display correctly"
echo "   - Thumbnails/previews show if available"
echo "   - Media counts display at bottom of cards"
echo "   - Filtering and search work properly"
echo ""

echo "================================"
echo "Database Verification Queries:"
echo "================================"
echo ""
echo "# Check projects"
echo "SELECT id, name, type, status, created_at FROM projects ORDER BY created_at DESC LIMIT 5;"
echo ""
echo "# Check exports for projects"
echo "SELECT p.name, e.file_path, e.format, e.created_at "
echo "FROM projects p JOIN exports e ON e.project_id = p.id "
echo "ORDER BY e.created_at DESC LIMIT 5;"
echo ""
echo "# Check thumbnails"
echo "SELECT p.name, i.file_path, i.type, i.created_at "
echo "FROM projects p JOIN images i ON i.project_id = p.id "
echo "WHERE i.type = 'thumbnail' "
echo "ORDER BY i.created_at DESC LIMIT 5;"
echo ""
echo "# Check media counts"
echo "SELECT "
echo "  p.name,"
echo "  COUNT(DISTINCT t.id) as tracks,"
echo "  COUNT(DISTINCT v.id) as videos,"
echo "  COUNT(DISTINCT i.id) as images"
echo "FROM projects p"
echo "LEFT JOIN tracks t ON t.project_id = p.id"
echo "LEFT JOIN videos v ON v.project_id = p.id"
echo "LEFT JOIN images i ON i.project_id = p.id"
echo "GROUP BY p.id, p.name"
echo "ORDER BY p.created_at DESC LIMIT 5;"
echo ""

echo "================================"
echo "Troubleshooting:"
echo "================================"
echo "If projects don't load:"
echo "  - Check browser console for errors"
echo "  - Verify auth token in localStorage"
echo "  - Check backend logs for errors"
echo "  - Verify database connection"
echo ""
echo "If images don't display:"
echo "  - Check S3 bucket permissions"
echo "  - Verify file paths in database"
echo "  - Check browser console for CORS errors"
echo "  - Verify S3 credentials in settings"
echo ""
echo "For more details, see: PROJECTS_PAGE_IMPROVEMENTS.md"
echo ""

