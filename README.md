# Audio Downloader for Diarization Training

A lightweight FastAPI service for downloading and storing audio files to train diarization models.

## 🎯 Purpose

This service is designed to:
- Download audio files from URLs
- Convert them to standardized WAV format (16kHz, mono)
- Store them locally with proper naming conventions
- **Track metadata in real-time** (duration, size, timestamps)
- **Monitor collection progress** toward target hours
- Log all operations for tracking and debugging

Perfect for collecting training data for diarization models!

## 📁 Project Structure

```
DOWNLOAD_DIA_AUDIOS/
├── main.py                      # FastAPI application with endpoints
├── audio_downloader.py          # Audio download and conversion logic
├── logger.py                    # Logging configuration
├── metadata_tracker.py          # Real-time metadata tracking
├── analyze_storage.py           # Storage analysis and progress monitoring
├── batch_download_from_csv.py   # Batch download script
├── test_single_download.py      # Single download test
├── hourly_monitor.sh            # Hourly monitoring script (cron)
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── USAGE_GUIDE.md              # CSV batch download guide
├── TRACKING_GUIDE.md           # Detailed tracking & monitoring guide
├── logs/                        # Log files directory (auto-created)
├── downloaded_audios/           # Downloaded audio files (auto-created)
└── conversations_metadata.json  # Live metadata tracking (auto-created)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd DOWNLOAD_DIA_AUDIOS
pip install -r requirements.txt
```

### 2. Set Up Environment (Optional)

```bash
cp .env.example .env
# Edit .env with your preferred settings
```

### 3. Run the Server

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8888 --reload
```

The API will be available at `http://localhost:8888`

### 4. Test with CSV Data (Recommended)

**Quick Test (1 conversation):**
```bash
python test_single_download.py
```

**Batch Download (all 13 conversations):**
```bash
python batch_download_from_csv.py
```

## 📊 Track Your Progress

Every conversation download is **automatically tracked** with:
- ✅ Conversation ID and timestamp
- ✅ Audio duration (seconds, minutes, hours)
- ✅ File sizes (MB/GB)
- ✅ File paths and URLs

**View current statistics:**
```bash
# API endpoint
curl http://localhost:8888/statistics

# Command line
python3 metadata_tracker.py

# Check progress toward target
python3 analyze_storage.py --target 100

# Export to CSV
python3 analyze_storage.py --export-csv
```

### Hourly Automated Monitoring

Set up automatic hourly checks:

```bash
chmod +x hourly_monitor.sh
nano hourly_monitor.sh  # Set TARGET_HOURS=100
crontab -e  # Add: 0 * * * * /path/to/DOWNLOAD_DIA_AUDIOS/hourly_monitor.sh
```

## 📡 API Endpoints

### 1. Root Endpoint
```
GET /
```
Returns API information and available endpoints.

### 2. Health Check
```
GET /health
```
Check if the service is running and get storage directory info.

### 3. Download Single Audio
```
POST /download/single
```

**Form Data:**
- `conversation_id` (required): Unique identifier for the conversation
- `audio_url` (required): URL of the audio file
- `speaker_label` (optional, default="speaker"): Label for the speaker

**Example using curl:**
```bash
curl -X POST "http://localhost:8888/download/single" \
  -F "conversation_id=conv_001" \
  -F "audio_url=https://example.com/audio.mp3" \
  -F "speaker_label=agent"
```

**Response:**
```json
{
  "status": "success",
  "conversation_id": "conv_001",
  "speaker_label": "agent",
  "filename": "conv_001_agent.wav",
  "filepath": "./downloaded_audios/conv_001_agent.wav",
  "file_size_mb": 2.45
}
```

### 4. Download Dual Audio (Agent + Customer)
```
POST /download/dual
```

**Form Data:**
- `conversation_id` (required): Unique identifier for the conversation
- `audio_url_agent` (required): URL of the agent's audio file
- `audio_url_customer` (optional): URL of the customer's audio file

**Example using curl:**
```bash
curl -X POST "http://localhost:8888/download/dual" \
  -F "conversation_id=conv_002" \
  -F "audio_url_agent=https://example.com/agent_audio.mp3" \
  -F "audio_url_customer=https://example.com/customer_audio.mp3"
```

**Response:**
```json
{
  "conversation_id": "conv_002",
  "status": "success",
  "total_files": 2,
  "downloads": [
    {
      "speaker": "agent",
      "filename": "conv_002_agent.wav",
      "filepath": "./downloaded_audios/conv_002_agent.wav",
      "file_size_mb": 2.45,
      "status": "success"
    },
    {
      "speaker": "customer",
      "filename": "conv_002_customer.wav",
      "filepath": "./downloaded_audios/conv_002_customer.wav",
      "file_size_mb": 1.89,
      "status": "success"
    }
  ]
}
```

### 5. Storage Information
```
GET /storage/info
```
Get information about stored audio files.

**Response:**
```json
{
  "storage_directory": "./downloaded_audios",
  "total_files": 42,
  "total_size_mb": 125.67,
  "files": ["conv_001_agent.wav", "conv_001_customer.wav", ...]
}
```

### 6. Statistics & Progress Tracking
```
GET /statistics?target_hours=100
```
Get comprehensive statistics about downloaded conversations with progress tracking.

**Response:**
```json
{
  "summary": {
    "total_conversations": 13,
    "total_hours": 10.25,
    "total_minutes": 615.0,
    "total_size_mb": 453.23,
    "total_size_gb": 0.44,
    "average_duration_minutes": 47.31,
    "average_size_mb": 34.86,
    "first_download": "2025-10-16T17:41:00",
    "last_download": "2025-10-16T17:55:30"
  },
  "progress": {
    "target_hours": 100.0,
    "current_hours": 10.25,
    "remaining_hours": 89.75,
    "progress_percentage": 10.3,
    "estimated_conversations_needed": 114,
    "target_reached": false
  },
  "timestamp": "2025-10-16T18:45:23"
}
```

## 📊 Interactive API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: `http://localhost:8888/docs`
- **ReDoc**: `http://localhost:8888/redoc`

## 🎵 Audio Processing

All downloaded audio files are automatically:
- Converted to WAV format
- Resampled to 16kHz
- Converted to mono (single channel)
- Saved with standardized naming: `{conversation_id}_{speaker_label}.wav`

## 📝 Logging

Logs are stored in `./logs/audio_downloader.log` with:
- Automatic rotation (5MB per file, keeping 3 backup files)
- Indian Standard Time (IST) timestamps
- Console and file output
- Detailed request/response tracking

**Log file location:** `./logs/audio_downloader.log`

## 🔧 Configuration

Environment variables (optional):

```bash
# Audio storage directory
AUDIO_STORAGE_DIR=./downloaded_audios

# Server port
PORT=8888

# Log directory
LOG_DIR=./logs
```

## 📦 Supported Audio Formats

Input formats:
- MP3 (audio/mpeg)
- WAV (audio/wav)
- OGG (audio/ogg)
- FLAC (audio/flac)
- AAC (audio/aac)
- M4A (audio/mp4)

Output format: WAV (16kHz, mono)

## 🛠️ Development

### Testing the API

You can test using:

1. **curl** (see examples above)
2. **Swagger UI** at `http://localhost:8888/docs`
3. **Python requests:**

```python
import requests

url = "http://localhost:8888/download/single"
data = {
    "conversation_id": "test_001",
    "audio_url": "https://example.com/audio.mp3",
    "speaker_label": "agent"
}
response = requests.post(url, data=data)
print(response.json())
```

### Running in Production

For production deployment, use a production-grade ASGI server:

```bash
uvicorn main:app --host 0.0.0.0 --port 8888 --workers 4
```

## 📈 Use Cases

1. **Collecting Training Data**: Download audio files for training diarization models with progress tracking
2. **Goal-Based Collection**: Set a target (e.g., 100 hours) and monitor progress
3. **Data Pipeline**: Part of an automated data collection pipeline
4. **Audio Preprocessing**: Standardize audio format before model training
5. **Backup & Archive**: Store audio files with consistent naming and metadata

## 🎯 Typical Workflow

1. **Set Your Goal**: Decide how many hours of audio you need (e.g., 100 hours)
2. **Start Downloading**: Run batch download script
3. **Track Progress**: Monitor in real-time via API or command line
4. **Hourly Checks**: Set up automated hourly monitoring
5. **Stop When Ready**: System tells you when target is reached
6. **Export Data**: Export metadata to CSV for analysis

**Example:**
```bash
# Start server
python3 main.py &

# Download all conversations
python3 batch_download_from_csv.py

# Check progress anytime
python3 analyze_storage.py --target 100

# When target reached, stop the service
```

## 📝 Metadata & Reports

### Files Generated

| File | Purpose | Auto-Created |
|------|---------|--------------|
| `conversations_metadata.json` | Live metadata for all downloads | ✅ Yes |
| `conversations_metadata.csv` | Metadata in CSV format | Via `--export-csv` |
| `storage_report_*.json` | Timestamped analysis reports | Via `--save` |
| `hourly_log.txt` | Hourly monitoring logs | Via cron |

### Metadata Fields

Each conversation entry includes:
- Conversation ID & timestamp
- Agent audio: filepath, URL, size, duration
- Customer audio: filepath, URL, size, duration
- Total: combined size, duration (seconds, minutes, hours)

## ⚠️ Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid URL, missing parameters)
- `500`: Internal server error

All errors are logged with detailed information for debugging.

## 🤝 Integration

This service can be integrated with:
- Data collection pipelines
- ML training workflows
- Audio preprocessing systems
- Voice analytics platforms

## 📞 Support

For issues or questions, check the logs at `./logs/audio_downloader.log` for detailed error messages.

## 🚀 Quick Commands Reference

```bash
# Start server
python3 main.py

# Test single download
python3 test_single_download.py

# Batch download from CSV
python3 batch_download_from_csv.py

# Check statistics
python3 metadata_tracker.py

# Analyze progress (100 hours target)
python3 analyze_storage.py --target 100

# Export metadata to CSV
python3 analyze_storage.py --export-csv

# API statistics
curl http://localhost:8888/statistics?target_hours=100

# API docs
open http://localhost:8888/docs
```

---

**Note**: This is a specialized audio downloader for collecting training data for diarization models, with comprehensive tracking and monitoring capabilities.

