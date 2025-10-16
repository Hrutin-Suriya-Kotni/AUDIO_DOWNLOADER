# Audio Downloader for Diarization Training

A lightweight FastAPI service for downloading and storing audio files to train diarization models.

## 🎯 Purpose

This service is designed to:
- Download audio files from URLs
- Convert them to standardized WAV format (16kHz, mono)
- Store them locally with proper naming conventions
- Log all operations for tracking and debugging

## 📁 Project Structure

```
DOWNLOAD_DIA_AUDIOS/
├── main.py                 # FastAPI application with endpoints
├── audio_downloader.py     # Audio download and conversion logic
├── logger.py              # Logging configuration
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
├── logs/                 # Log files directory (auto-created)
└── downloaded_audios/    # Downloaded audio files (auto-created)
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
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

The API will be available at `http://localhost:8001`

### 4. Test with CSV Data (Recommended)

**Quick Test (1 conversation):**
```bash
python test_single_download.py
```

**Batch Download (all 13 conversations):**
```bash
python batch_download_from_csv.py
```

See `USAGE_GUIDE.md` for detailed instructions.

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
curl -X POST "http://localhost:8001/download/single" \
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
curl -X POST "http://localhost:8001/download/dual" \
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

## 📊 Interactive API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`

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
PORT=8001

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
2. **Swagger UI** at `http://localhost:8001/docs`
3. **Python requests:**

```python
import requests

url = "http://localhost:8001/download/single"
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
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
```

## 📈 Use Cases

1. **Collecting Training Data**: Download audio files for training diarization models
2. **Data Pipeline**: Part of an automated data collection pipeline
3. **Audio Preprocessing**: Standardize audio format before model training
4. **Backup & Archive**: Store audio files with consistent naming conventions

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

---

**Note**: This is a simplified version of the full Voice2Chat service, focused only on audio downloading and storage for training purposes.

