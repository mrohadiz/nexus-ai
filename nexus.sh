#!/bin/bash

# Nexus AI Service Manager (PM2 Edition)
# Usage: ./nexus.sh [start|stop|restart|status|logs]

export PATH="/root/.bun/bin:$PATH"
PROJECT_ROOT="/root/nexus-ai"
CONFIG="$PROJECT_ROOT/ecosystem.config.js"

case "$1" in
    start)
        pm2 start "$CONFIG"
        ;;
    stop)
        pm2 stop "$CONFIG"
        ;;
    restart)
        pm2 restart "$CONFIG"
        ;;
    status)
        pm2 status
        echo ""
        service postgresql status | grep "Active:"
        ;;
    logs)
        pm2 logs
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        exit 1
esac
