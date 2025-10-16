# Audio Collection Tracking & Monitoring Guide

This guide explains how to track and monitor your audio collection progress in real-time.

## 🎯 Overview

The system provides **two layers of tracking**:

1. **Live Metadata Tracking** - Automatically tracks each conversation as it's downloaded
2. **Periodic Analysis** - Analyze progress hourly or on-demand to monitor your goal

---

## 📊 Features

### 1. Real-Time Metadata Tracking

Every time a conversation (agent + customer audio) is downloaded, the system automatically saves:
- Conversation ID
- Download timestamp
- File sizes (agent, customer, total)
- Audio durations (seconds, minutes, hours)
- File paths
- Source URLs

**Storage**: `conversations_metadata.json` (appended in real-time)

### 2. Progress Analysis

Track your progress toward a target number of hours:
- Total hours collected
- Number of conversations
- Storage used (MB/GB)
- Progress percentage
- Estimated conversations remaining
- Download rate statistics

---

## 🚀 Quick Start

### Step 1: Set Your Target

Decide how many hours of audio you need. For example: **100 hours**

### Step 2: Start Downloading

Run the batch download:
```bash
python3 batch_download_from_csv.py
```

**Metadata is automatically tracked** as each conversation downloads! ✅

### Step 3: Check Progress Anytime

**Option A: Command Line**
```bash
# Basic statistics
python3 analyze_storage.py

# With target tracking
python3 analyze_storage.py --target 100

# Save report to JSON
python3 analyze_storage.py --target 100 --save

# Export to CSV
python3 analyze_storage.py --export-csv
```

**Option B: API Endpoint**
```bash
# Get statistics
curl http://localhost:8888/statistics

# Get statistics with target
curl "http://localhost:8888/statistics?target_hours=100"
```

**Option C: Python Script**
```python
from metadata_tracker import MetadataTracker

tracker = MetadataTracker()
stats = tracker.get_statistics()

print(f"Total Hours: {stats['total_hours']:.2f}")
print(f"Total Conversations: {stats['total_conversations']}")
print(f"Storage: {stats['total_size_gb']:.2f} GB")
```

---

## ⏰ Hourly Monitoring (Automated)

### Setup Cron Job

To automatically check progress every hour:

1. **Make the script executable:**
```bash
chmod +x hourly_monitor.sh
```

2. **Edit the script to set your target:**
```bash
nano hourly_monitor.sh
# Change: TARGET_HOURS=100 to your target
```

3. **Add to crontab:**
```bash
crontab -e
```

Add this line:
```
0 * * * * /Users/cleveres_tidiot/Documents/Vocab_AI/DOWNLOAD_DIA_AUDIOS/hourly_monitor.sh >> /Users/cleveres_tidiot/Documents/Vocab_AI/DOWNLOAD_DIA_AUDIOS/hourly_log.txt 2>&1
```

This will:
- Run every hour at minute 0
- Generate a detailed report
- Save reports to `storage_report_*.json`
- Log output to `hourly_log.txt`

---

## 📈 Sample Output

### Command Line Analysis

```
======================================================================
                  AUDIO STORAGE ANALYSIS REPORT
======================================================================
Generated: 2025-10-16 18:45:23
======================================================================

📊 SUMMARY:
  Total Conversations Downloaded: 13
  Total Audio Duration:           10.25 hours (615.0 minutes)
  Total Storage Used:             0.44 GB (453.23 MB)

📈 AVERAGES:
  Average Conversation Duration:  47.31 minutes
  Average Conversation Size:      34.86 MB

🎯 PROGRESS TO TARGET:
  Target Hours:                   100.00 hours
  Current Hours:                  10.25 hours
  Remaining Hours:                89.75 hours
  Progress:                       10.3%
  [████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 10.3%

  📥 Estimated conversations needed: 114

⏰ TIMELINE:
  First Download:                 2025-10-16T17:41:00
  Last Download:                  2025-10-16T17:55:30
  Download Duration:              0.24 hours
  Download Rate:                  54.17 conversations/hour
  Audio Collection Rate:          42.71 hours of audio/hour

💾 STORAGE BREAKDOWN:
  Agent Audio:                    226.61 MB
  Customer Audio:                 226.61 MB

======================================================================
```

### API Response

```json
{
  "summary": {
    "total_conversations": 13,
    "total_hours": 10.25,
    "total_minutes": 615.0,
    "total_size_mb": 453.23,
    "total_size_gb": 0.44,
    "average_duration_minutes": 47.31,
    "average_size_mb": 34.86
  },
  "progress": {
    "target_hours": 100,
    "current_hours": 10.25,
    "remaining_hours": 89.75,
    "progress_percentage": 10.3,
    "estimated_conversations_needed": 114,
    "target_reached": false
  }
}
```

---

## 📁 Files Created

| File | Purpose |
|------|---------|
| `conversations_metadata.json` | **Live metadata** - Updated in real-time as conversations download |
| `conversations_metadata.csv` | Metadata exported to CSV (create with `--export-csv`) |
| `storage_report_*.json` | Hourly analysis reports (timestamped) |
| `hourly_log.txt` | Log of hourly monitoring runs |

---

## 🔧 Metadata Structure

Each conversation entry contains:

```json
{
  "conversation_id": "e587124c-02b6-49c5-b3bf-2610015da46a",
  "timestamp": "2025-10-16T17:41:00",
  "agent": {
    "filepath": "./downloaded_audios/..._agent.wav",
    "url": "https://...",
    "size_mb": 21.47,
    "duration_seconds": 703.4,
    "duration_minutes": 11.72
  },
  "customer": {
    "filepath": "./downloaded_audios/..._customer.wav",
    "url": "https://...",
    "size_mb": 21.47,
    "duration_seconds": 703.4,
    "duration_minutes": 11.72
  },
  "total": {
    "size_mb": 42.94,
    "duration_seconds": 703.4,
    "duration_minutes": 11.72,
    "duration_hours": 0.1953
  }
}
```

---

## 🎯 Usage Scenarios

### Scenario 1: Track to 100 Hours

```bash
# Check progress anytime
python3 analyze_storage.py --target 100

# When it shows "Target reached", stop your download service
```

### Scenario 2: Monitor Multiple Targets

```bash
# Check different targets
python3 analyze_storage.py --target 50   # First milestone
python3 analyze_storage.py --target 100  # Final goal
python3 analyze_storage.py --target 200  # Stretch goal
```

### Scenario 3: Daily Reports

```bash
# Generate and save daily report
python3 analyze_storage.py --target 100 --save --export-csv
```

---

## 🛑 When to Stop

The system will tell you when target is reached:

```
✅ TARGET REACHED! You can stop the download service.
```

Then you can:
1. Stop the FastAPI server
2. Stop batch download scripts
3. Export final metadata to CSV
4. Archive the audio files

---

## 💡 Pro Tips

1. **Set Realistic Targets**: Based on average ~0.2 hours per conversation, 100 hours ≈ 500 conversations
2. **Monitor Storage**: ~1.83 MB per minute → 100 hours ≈ 11 GB
3. **Check Progress Daily**: Even with hourly cron, manually check once a day
4. **Export Metadata**: Use `--export-csv` for analysis in Excel/Google Sheets
5. **Backup Metadata**: The `conversations_metadata.json` file is precious - back it up!

---

## 🐛 Troubleshooting

**Q: Metadata not tracking?**
- A: Check that the FastAPI server is running with the updated code
- A: Only dual downloads (agent + customer) are tracked, not single files

**Q: Wrong duration calculated?**
- A: Ensure pydub is installed: `pip install pydub`
- A: Check that ffmpeg is available (for non-WAV formats)

**Q: Can't find conversations_metadata.json?**
- A: It's created after the first dual download completes
- A: Check you're in the correct directory

**Q: How to reset tracking?**
- A: Delete or rename `conversations_metadata.json` to start fresh
- A: Or manually edit the JSON file to remove entries

---

## 📞 Quick Reference

```bash
# Check current status
python3 metadata_tracker.py

# Analyze with target
python3 analyze_storage.py --target 100

# Export data
python3 analyze_storage.py --export-csv

# API statistics
curl http://localhost:8888/statistics?target_hours=100

# Setup hourly monitoring
chmod +x hourly_monitor.sh
crontab -e  # Add hourly job
```

---

**Ready to track your audio collection!** 🎵📊

