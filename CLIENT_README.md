# Audio Uploader - Client Guide

**Super simple way to upload your audio files to the server!**

---

## 📋 What You Need

1. A CSV file with your audio URLs
2. Python 3 installed
3. Internet connection

That's it! 🎉

---

## 🚀 Quick Start

### Step 1: Install Requirements

```bash
pip install requests
```

### Step 2: Prepare Your CSV File

Create a CSV file with this format:

```csv
conversation_id,agent_url,customer_url
conv_001,https://drive.google.com/uc?export=download&id=ABC123,https://drive.google.com/uc?export=download&id=DEF456
conv_002,https://drive.google.com/uc?export=download&id=GHI789,https://drive.google.com/uc?export=download&id=JKL012
```

**Required columns:**
- `conversation_id` - Unique ID for each conversation
- `agent_url` - URL to agent audio file
- `customer_url` - URL to customer audio file (optional)

### Step 3: Run the Script

```bash
python3 client_uploader.py --csv your_file.csv
```

**That's it!** ✅

---

## 📺 What You'll See

```
============================================================
  Audio Uploader - Send Files to Server
============================================================

Server: http://27.111.72.52:8888
Time: 2025-10-22 12:30:00

✓ Server is online and ready

✓ Found 10 conversations to upload

Starting upload...

[1/10] Processing: conv_001...
  ✓ Success! Uploaded 2 files in 45.2s
    → agent: 21.47 MB
    → customer: 21.47 MB

[2/10] Processing: conv_002...
  ✓ Success! Uploaded 2 files in 38.1s
    → agent: 18.52 MB
    → customer: 18.52 MB

...

============================================================
  Upload Complete!
============================================================

Total conversations: 10
Successful: 10
Failed: 0
Total time: 425.5s
Average: 42.6s per conversation
```

---

## 📝 Example CSV Files

### Example 1: Simple CSV

**my_conversations.csv:**
```csv
conversation_id,agent_url,customer_url
test_001,https://example.com/agent1.mp3,https://example.com/customer1.mp3
test_002,https://example.com/agent2.mp3,https://example.com/customer2.mp3
```

**Run:**
```bash
python3 client_uploader.py --csv my_conversations.csv
```

### Example 2: With Full Google Drive URLs

**google_drive_files.csv:**
```csv
conversation_id,agent_url,customer_url
e587124c-02b6-49c5-b3bf-2610015da46a,https://drive.google.com/uc?export=download&id=1cHuqbFn_AJlWyx8YlB2uvIKgm-U2JxOt,https://drive.google.com/uc?export=download&id=1HCEzRL04kUarScOpkk4rnzR3TYFeVprG
```

**Run:**
```bash
python3 client_uploader.py --csv google_drive_files.csv
```

---

## ❓ Troubleshooting

### "Cannot connect to server"
- Check your internet connection
- Ask the developer if server is running

### "CSV file not found"
- Make sure the file path is correct
- Use full path: `python3 client_uploader.py --csv /full/path/to/file.csv`

### "No valid conversations found"
- Check your CSV has the correct columns: `conversation_id`, `agent_url`, `customer_url`
- Make sure there's data in the file (not just headers)

### Upload timeout
- Large files take time (normal for 20+ MB files)
- Script waits up to 5 minutes per conversation
- If it times out, it will continue to next one

---

## 🎯 Tips

1. **Start small**: Test with 1-2 conversations first
2. **Check CSV**: Make sure URLs are correct and accessible
3. **Be patient**: Large files take time to upload
4. **Let it run**: You can leave it running - it will finish all conversations

---

## 📊 Check Your Progress

After uploading, check how much data you've collected:

```bash
curl "http://27.111.72.52:8888/statistics?target_hours=100"
```

Or open in browser:
```
http://27.111.72.52:8888/docs
```

---

## 🆘 Need Help?

Contact the developer with:
- Your CSV file (first few lines)
- Error message you're seeing
- What you've tried

---

## ✅ That's It!

**Three simple steps:**
1. Create CSV file
2. Run `python3 client_uploader.py --csv file.csv`
3. Wait for completion

**No complexity. Just upload and go!** 🚀

