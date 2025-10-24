#!/bin/bash
# Hourly Analytics Cron Script
# Add to crontab: 0 * * * * /path/to/hourly_analytics_cron.sh

# Change to project directory
cd "$(dirname "$0")"

# Set target hours (modify this)
TARGET_HOURS=100

# Activate virtual environment if exists
if [ -d ".down_env" ]; then
    source .down_env/bin/activate
elif [ -d "down_env" ]; then
    source down_env/bin/activate
fi

# Run hourly analytics
echo "========================================"
echo "Hourly Analytics - $(date)"
echo "========================================"

python3 hourly_analytics.py --target $TARGET_HOURS

echo "========================================"
echo ""

