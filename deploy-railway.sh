#!/bin/bash

# GIMAT Railway Deployment Script
# Run this to deploy to Railway.app

set -e

echo "========================================"
echo "GIMAT Railway Deployment"
echo "========================================"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway
echo "Logging in to Railway..."
railway login

# Initialize project (if not already)
if [ ! -f "railway.json" ]; then
    echo "Initializing Railway project..."
    railway init
fi

# Deploy
echo "Deploying to Railway..."
railway up

# Show deployment URL
echo ""
echo "========================================"
echo "Deployment successful! ✓"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Add environment variables: railway variables"
echo "2. Add PostgreSQL: railway add postgres"
echo "3. Add Redis: railway add redis"
echo "4. View logs: railway logs"
echo "5. Open dashboard: railway open"
echo ""
echo "Don't forget to set these variables:"
echo "  - NEO4J_URI"
echo "  - NEO4J_USER"
echo "  - NEO4J_PASSWORD"
echo "  - OPENAI_API_KEY"
echo ""
