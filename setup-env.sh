#!/bin/bash

# Setup environment variables for Clipizy
echo "Setting up environment variables for Clipizy..."

# Create .env.local file for Next.js
cat > .env.local << EOF
# Frontend Environment Variables
NEXT_PUBLIC_AUTH_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXItaWQiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20iLCJuYW1lIjoiVGVzdCBVc2VyIiwiZXhwIjoxNzYwNDY3Njc0LCJ0eXBlIjoiYWNjZXNzIn0.ujC21qDkX5QtaWMSx4-Mp3QOo1my6z1wIspONwl98qE

# Backend URL
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
EOF

echo "✅ Created .env.local file with authentication token"
echo "✅ Auth token will now be loaded from environment variables instead of localStorage"
echo ""
echo "To use a different token, edit the NEXT_PUBLIC_AUTH_TOKEN value in .env.local"
echo "To use a different backend URL, edit the NEXT_PUBLIC_BACKEND_URL value in .env.local"
echo ""
echo "Restart your Next.js development server for changes to take effect."
