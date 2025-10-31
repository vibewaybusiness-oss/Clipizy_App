#!/bin/bash

# Start Next.js with proper host binding for WSL
echo "🚀 Starting Next.js with WSL-compatible host binding..."
npx next dev -H 0.0.0.0 -p 3000
