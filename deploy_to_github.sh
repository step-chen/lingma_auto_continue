#!/bin/bash

# Deploy to GitHub script
# Please replace YOUR_USERNAME and YOUR_REPOSITORY with your actual GitHub username and repository name

echo "Deploying to GitHub..."

# Add remote origin (please replace with your actual GitHub username and repo name)
git remote add origin https://github.com/step-chen/lingma_auto_continue.git

# Rename branch to main (GitHub's default)
git branch -M main

# Push to GitHub
git push -u origin main

echo "Deployment complete!"
echo ""
echo "If you get authentication errors, you may need to:"
echo "1. Use GitHub CLI: gh auth login"
echo "2. Or set up SSH keys"
echo "3. Or use personal access token"