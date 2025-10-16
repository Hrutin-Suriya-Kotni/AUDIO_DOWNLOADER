# Usage Guide - Audio Downloader

This guide shows you how to use the audio downloader with the provided CSV file.

## 📋 CSV File Format

The `paired_conversation_urls.csv` contains:
- **conversation_id**: Original UUID from the system
- **customer_url**: Google Drive URL for customer audio
- **agent_url**: Google Drive URL for agent audio
- **customer_filename**: Original customer filename
- **agent_filename**: Original agent filename

## 🚀 Quick Start

### Step 1: Start the Server

```bash
cd /Users/cleveres_tidiot/Documents/Vocab_AI/DOWNLOAD_DIA_AUDIOS
python main.py
```

The server will start at `http://localhost:8001`

### Step 2: Test with One Conversation

Test with the first conversation from the CSV:

```bash
python test_single_download.py
```

This will:
- Read the first row from `paired_conversation_urls.csv`
- Use conversation ID: `test_conv_01`
- Download both customer and agent audio files
- Show the results

### Step 3: Download All Conversations (Batch)

Download all 13 conversations from the CSV:

```bash
python batch_download_from_csv.py
```

This will:
- Read all conversations from the CSV
- Assign IDs like `test_conv_01`, `test_conv_02`, etc.
- Download all audio files (26 total: 13 agent + 13 customer)
- Show progress for each download
- Save a detailed results JSON file

## 📁 Output Files

After running the batch download:

### Downloaded Audio Files
Location: `./downloaded_audios/`

Files will be named:
- `test_conv_01_agent.wav`
- `test_conv_01_customer.wav`
- `test_conv_02_agent.wav`
- `test_conv_02_customer.wav`
- ... and so on

### Results File
Location: `./download_results_YYYYMMDD_HHMMSS.json`

Contains:
```json
{
  "start_time": "2025-10-16T...",
  "csv_file": "paired_conversation_urls.csv",
  "total_conversations": 13,
  "successful": 13,
  "failed": 0,
  "details": [
    {
      "conversation_id": "test_conv_01",
      "original_id": "e587124c-02b6-49c5-b3bf-2610015da46a",
      "success": true,
      "duration_seconds": 5.23,
      "response": { ... }
    },
    ...
  ]
}
```

### Log Files
Location: `./logs/audio_downloader.log`

Contains detailed logs of all operations.

## 📊 Example Output

### Single Download Test
```
============================================================
Testing Single Audio Download
============================================================

Original Conversation ID: e587124c-02b6-49c5-b3bf-2610015da46a
Customer URL: https://drive.google.com/uc?export=download&id=1HCE...
Agent URL: https://drive.google.com/uc?export=download&id=1cHu...

Using test conversation ID: test_conv_01

1. Checking server health...
   ✓ Server is running

2. Downloading audio files...
   Status Code: 200
   
   ✓ Download successful!
   
   Response:
   {
     "conversation_id": "test_conv_01",
     "status": "success",
     "total_files": 2,
     "downloads": [...]
   }
```

### Batch Download
```
======================================================================
  Batch Audio Downloader from CSV
======================================================================

Checking server status...
✓ Server is healthy and running

Reading CSV file...
Found 13 conversations to process

Starting batch download...

[1/13] Processing test_conv_01...
✓ SUCCESS: test_conv_01 (took 5.2s)
  └─ agent    → test_conv_01_agent.wav (2.45 MB)
  └─ customer → test_conv_01_customer.wav (1.89 MB)

[2/13] Processing test_conv_02...
✓ SUCCESS: test_conv_02 (took 4.8s)
  └─ agent    → test_conv_02_agent.wav (3.12 MB)
  └─ customer → test_conv_02_customer.wav (2.67 MB)

...

======================================================================
  SUMMARY
======================================================================
Total conversations: 13
Successful:         13
Failed:             0
Total duration:     67.4s
Average per conv:   5.2s

Results saved to: download_results_20251016_143022.json

✓ Batch download complete!
```

## 🔧 Conversation ID Mapping

The script automatically converts UUIDs to simple test IDs:

| Original UUID                          | New Test ID    |
|---------------------------------------|----------------|
| e587124c-02b6-49c5-b3bf-2610015da46a | test_conv_01   |
| f2e84be9-b188-4658-bcaa-666642b4620f | test_conv_02   |
| d3bb1e69-6685-413f-873a-d8cd263f08cf | test_conv_03   |
| ... | ... |

This makes it easier to work with the files while maintaining the mapping in the results JSON.

## 🎯 Manual API Testing

You can also test manually with curl:

```bash
# Download single file
curl -X POST "http://localhost:8001/download/single" \
  -F "conversation_id=test_conv_01" \
  -F "audio_url=https://drive.google.com/uc?export=download&id=1HCEzRL04kUarScOpkk4rnzR3TYFeVprG" \
  -F "speaker_label=customer"

# Download dual files
curl -X POST "http://localhost:8001/download/dual" \
  -F "conversation_id=test_conv_01" \
  -F "audio_url_agent=https://drive.google.com/uc?export=download&id=1cHuqbFn_AJlWyx8YlB2uvIKgm-U2JxOt" \
  -F "audio_url_customer=https://drive.google.com/uc?export=download&id=1HCEzRL04kUarScOpkk4rnzR3TYFeVprG"

# Check storage
curl http://localhost:8001/storage/info
```

## 📊 Interactive API Docs

Visit `http://localhost:8001/docs` for interactive Swagger UI where you can:
- Test all endpoints
- See request/response schemas
- Try different parameters

## ⏱️ Performance Notes

- Average download time: ~5 seconds per conversation (2 audio files)
- Total time for 13 conversations: ~1-2 minutes
- Includes 1-second delay between requests
- Google Drive direct download links are used for faster downloads

## 🐛 Troubleshooting

### Server not running
```
✗ Cannot connect to server at http://localhost:8001
```
**Solution**: Start the server with `python main.py`

### Download timeout
```
✗ Request timed out
```
**Solution**: The script has a 120-second timeout. If files are very large, you may need to increase it.

### Invalid audio URL
```
Failed to download audio from provided URL
```
**Solution**: Check that the Google Drive links are publicly accessible.

---

**Ready to start?** Run `python test_single_download.py` to test with one file! 🚀

