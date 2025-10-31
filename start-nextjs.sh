#!/bin/bash

# Start Next.js development server
cd /root/clipizy

# Set environment variables to avoid UNC path issues
export NODE_OPTIONS="--max-old-space-size=4096"
export NEXT_TELEMETRY_DISABLED=1

# If nvm is installed, load it and try to use Node 18+
if [ -z "${NVM_DIR:-}" ]; then
    export NVM_DIR="$HOME/.nvm"
fi
if [ -s "$NVM_DIR/nvm.sh" ]; then
    . "$NVM_DIR/nvm.sh"
    if command -v nvm >/dev/null 2>&1; then
        nvm use 18 >/dev/null 2>&1 || true
    fi
fi

# Enforce Node.js version >= 18 to avoid syntax errors like "Unexpected token ?"
REQUIRED_NODE_MAJOR=18
if command -v node >/dev/null 2>&1; then
    NODE_VER=$(node -v 2>/dev/null | sed 's/^v//')
    NODE_MAJOR=${NODE_VER%%.*}
    if [ "$NODE_MAJOR" -lt "$REQUIRED_NODE_MAJOR" ]; then
        echo "Node.js $NODE_VER detected. Please install Node.js >= $REQUIRED_NODE_MAJOR."
        echo "You can use nvm: nvm install $REQUIRED_NODE_MAJOR && nvm use $REQUIRED_NODE_MAJOR"
        exit 1
    fi
else
    echo "Node.js not found. Please install Node.js >= $REQUIRED_NODE_MAJOR."
    exit 1
fi

# Check if node_modules exists, if not install dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

# Start Next.js development server
echo "Starting Next.js development server..."

# Try different methods to start Next.js, but only use one method
if command -v npx >/dev/null 2>&1; then
    echo "Using npx next dev with WSL host binding..."
    npx --yes next dev -H 0.0.0.0
elif [ -f "./node_modules/.bin/next" ]; then
    echo "Using local next binary with WSL host binding..."
    ./node_modules/.bin/next dev -H 0.0.0.0
else
    echo "Using node directly with WSL host binding..."
    node ./node_modules/next/dist/bin/next dev -H 0.0.0.0
fi
