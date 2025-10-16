#!/bin/bash

# Hourly Monitor Script
# Run this script every hour using cron to monitor download progress
#
# To set up hourly monitoring, add to crontab:
# 0 * * * * /path/to/DOWNLOAD_DIA_AUDIOS/hourly_monitor.sh

# Change to script directory
cd "$(dirname "$0")"

# Set your target hours here
TARGET_HOURS=100

# Activate virtual environment if it exists
if [ -d "down_env" ]; then
    source down_env/bin/activate
fi

# Run analysis
echo "========================================"
echo "HOURLY PROGRESS CHECK - $(date)"
echo "========================================"

python3 analyze_storage.py --target $TARGET_HOURS --save

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ Target reached! Download service can be stopped."
else
    echo "⏳ Keep downloading..."
fi

echo "========================================"

