#!/bin/bash
# Deploy script for Home Assistant nginx configuration
# Run this after 'git pull' to apply configuration changes

set -e  # Exit on error

REPO_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
NGINX_AVAILABLE="/etc/nginx/sites-available"
NGINX_ENABLED="/etc/nginx/sites-enabled"
CONFIG_NAME="hass"

echo "🚀 Starting Home Assistant nginx deployment..."
echo ""

# Check if running as root (sudo)
if [ "$EUID" -ne 0 ]; then 
    echo "❌ This script must be run with sudo"
    exit 1
fi

# Verify source file exists
if [ ! -f "$REPO_DIR/nginx/sites-available/$CONFIG_NAME" ]; then
    echo "❌ Source config not found: $REPO_DIR/nginx/sites-available/$CONFIG_NAME"
    exit 1
fi

echo "📋 Step 1: Copying config to sites-available..."
cp -p "$REPO_DIR/nginx/sites-available/$CONFIG_NAME" "$NGINX_AVAILABLE/$CONFIG_NAME"
echo "✅ Config copied to $NGINX_AVAILABLE/$CONFIG_NAME"
echo ""

echo "📋 Step 2: Copying config to sites-enabled..."
cp -p "$REPO_DIR/nginx/sites-available/$CONFIG_NAME" "$NGINX_ENABLED/$CONFIG_NAME"
echo "✅ Config copied to $NGINX_ENABLED/$CONFIG_NAME"
echo ""

echo "🔍 Step 3: Testing nginx configuration..."
if ! nginx -t 2>&1 | grep -q "successful"; then
    echo "❌ Nginx configuration test failed!"
    exit 1
fi
echo "✅ Configuration test passed"
echo ""

echo "🔄 Step 4: Reloading nginx..."
systemctl reload nginx
echo "✅ Nginx reloaded successfully"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Deployment successful!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Nginx status:"
systemctl status nginx --no-pager | head -5
echo ""
echo "Configuration details:"
echo "  Source:  $REPO_DIR/nginx/sites-available/$CONFIG_NAME"
echo "  Deployed to:"
echo "    - $NGINX_AVAILABLE/$CONFIG_NAME"
echo "    - $NGINX_ENABLED/$CONFIG_NAME"
echo ""
echo "Files are copies (not symlinks) for reliability and simplicity."
echo ""

