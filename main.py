"""
FastAPI Application for Downloading Diarization Audio Files
Purpose: Download and store audio files for training diarization models
"""

import os
from typing import Optional
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse

from audio_downloader import AudioHelper
from logger import get_logger

# Initialize logger
LOGGER = get_logger("AudioDownloader")

# Configuration
AUDIO_STORAGE_DIR = os.getenv("AUDIO_STORAGE_DIR", "./downloaded_audios")
os.makedirs(AUDIO_STORAGE_DIR, exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title="Audio Downloader API",
    description="API for downloading and storing audio files for diarization model training",
    version="1.0.0"
)

# Initialize AudioHelper (store_audio=False because we handle saving in the endpoints)
audio_helper = AudioHelper(store_audio=False)


@app.get("/")
def index():
    """Root endpoint - API information"""
    return {
        "service": "Audio Downloader API",
        "version": "1.0.0",
        "description": "Download and store audio files for training diarization models",
        "endpoints": {
            "/download/single": "Download single audio file",
            "/download/dual": "Download two audio files (agent + customer)",
            "/health": "Health check"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "storage_dir": AUDIO_STORAGE_DIR}


@app.post("/download/single")
async def download_single_audio(
    conversation_id: str = Form(..., description="Unique conversation identifier"),
    audio_url: str = Form(..., description="URL of the audio file to download"),
    speaker_label: str = Form(default="speaker", description="Label for the speaker (e.g., agent, customer)")
):
    """
    Download a single audio file and store it locally.
    
    Args:
        conversation_id: Unique identifier for the conversation
        audio_url: URL of the audio file
        speaker_label: Label to identify the speaker (default: "speaker")
    
    Returns:
        JSON response with download status and file path
    """
    LOGGER.info(f"Received download request for conversation_id: {conversation_id}")
    LOGGER.info(f"Audio URL: {audio_url}")
    LOGGER.info(f"Speaker label: {speaker_label}")
    
    try:
        # Download audio
        audio_data = audio_helper.download_audio(audio_url)
        if audio_data is None:
            LOGGER.error(f"Failed to download audio from URL: {audio_url}")
            raise HTTPException(status_code=400, detail="Failed to download audio from provided URL")
        
        # Save audio file
        filename = f"{conversation_id}_{speaker_label}.wav"
        filepath = os.path.join(AUDIO_STORAGE_DIR, filename)
        
        with open(filepath, 'wb') as f:
            f.write(audio_data.getvalue())
        
        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        
        LOGGER.info(f"Successfully saved audio file: {filepath} ({file_size_mb:.2f} MB)")
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "conversation_id": conversation_id,
                "speaker_label": speaker_label,
                "filename": filename,
                "filepath": filepath,
                "file_size_mb": round(file_size_mb, 2)
            }
        )
    
    except Exception as e:
        LOGGER.error(f"Error downloading audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/download/dual")
async def download_dual_audio(
    conversation_id: str = Form(..., description="Unique conversation identifier"),
    audio_url_agent: str = Form(..., description="URL of the agent audio file"),
    audio_url_customer: Optional[str] = Form(None, description="URL of the customer audio file (optional)")
):
    """
    Download two audio files (agent and customer) for diarization training.
    
    Args:
        conversation_id: Unique identifier for the conversation
        audio_url_agent: URL of the agent's audio file
        audio_url_customer: URL of the customer's audio file (optional)
    
    Returns:
        JSON response with download status for both files
    """
    LOGGER.info(f"Received dual download request for conversation_id: {conversation_id}")
    LOGGER.info(f"Agent audio URL: {audio_url_agent}")
    LOGGER.info(f"Customer audio URL: {audio_url_customer}")
    
    results = {
        "conversation_id": conversation_id,
        "downloads": []
    }
    
    try:
        # Download agent audio
        LOGGER.info("Downloading agent audio...")
        audio_data_agent = audio_helper.download_audio(audio_url_agent)
        if audio_data_agent is None:
            LOGGER.error(f"Failed to download agent audio from URL: {audio_url_agent}")
            raise HTTPException(status_code=400, detail="Failed to download agent audio")
        
        # Save agent audio
        filename_agent = f"{conversation_id}_agent.wav"
        filepath_agent = os.path.join(AUDIO_STORAGE_DIR, filename_agent)
        
        with open(filepath_agent, 'wb') as f:
            f.write(audio_data_agent.getvalue())
        
        file_size_agent_mb = os.path.getsize(filepath_agent) / (1024 * 1024)
        LOGGER.info(f"Successfully saved agent audio: {filepath_agent} ({file_size_agent_mb:.2f} MB)")
        
        results["downloads"].append({
            "speaker": "agent",
            "filename": filename_agent,
            "filepath": filepath_agent,
            "file_size_mb": round(file_size_agent_mb, 2),
            "status": "success"
        })
        
        # Download customer audio if provided
        if audio_url_customer:
            LOGGER.info("Downloading customer audio...")
            audio_data_customer = audio_helper.download_audio(audio_url_customer)
            if audio_data_customer is None:
                LOGGER.warning(f"Failed to download customer audio from URL: {audio_url_customer}")
                results["downloads"].append({
                    "speaker": "customer",
                    "status": "failed",
                    "error": "Failed to download audio"
                })
            else:
                # Save customer audio
                filename_customer = f"{conversation_id}_customer.wav"
                filepath_customer = os.path.join(AUDIO_STORAGE_DIR, filename_customer)
                
                with open(filepath_customer, 'wb') as f:
                    f.write(audio_data_customer.getvalue())
                
                file_size_customer_mb = os.path.getsize(filepath_customer) / (1024 * 1024)
                LOGGER.info(f"Successfully saved customer audio: {filepath_customer} ({file_size_customer_mb:.2f} MB)")
                
                results["downloads"].append({
                    "speaker": "customer",
                    "filename": filename_customer,
                    "filepath": filepath_customer,
                    "file_size_mb": round(file_size_customer_mb, 2),
                    "status": "success"
                })
        
        results["status"] = "success"
        results["total_files"] = len([d for d in results["downloads"] if d["status"] == "success"])
        
        return JSONResponse(status_code=200, content=results)
    
    except Exception as e:
        LOGGER.error(f"Error downloading audio files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/storage/info")
def storage_info():
    """Get information about stored audio files"""
    try:
        files = [f for f in os.listdir(AUDIO_STORAGE_DIR) if f.endswith('.wav')]
        total_size_mb = sum(
            os.path.getsize(os.path.join(AUDIO_STORAGE_DIR, f)) 
            for f in files
        ) / (1024 * 1024)
        
        return {
            "storage_directory": AUDIO_STORAGE_DIR,
            "total_files": len(files),
            "total_size_mb": round(total_size_mb, 2),
            "files": files[:50]  # Return first 50 files
        }
    except Exception as e:
        LOGGER.error(f"Error getting storage info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8001"))
    LOGGER.info(f"Starting Audio Downloader API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

