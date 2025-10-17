"""
FastAPI Application for Downloading Diarization Audio Files
Purpose: Download and store audio files for training diarization models
"""

import os
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from audio_downloader import AudioHelper
from logger import get_logger
from metadata_tracker import MetadataTracker

# Load environment variables from .env file
load_dotenv()

# Initialize logger and metadata tracker
LOGGER = get_logger("AudioDownloader")
metadata_tracker = MetadataTracker()

# Configuration
AUDIO_STORAGE_DIR = os.getenv("AUDIO_STORAGE_DIR", "./downloaded_audios")
os.makedirs(AUDIO_STORAGE_DIR, exist_ok=True)
LOGGER.info(f"Audio storage directory: {AUDIO_STORAGE_DIR}")

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
        
        # Create conversation folder
        conversation_folder = os.path.join(AUDIO_STORAGE_DIR, conversation_id)
        os.makedirs(conversation_folder, exist_ok=True)
        
        # Save audio file in conversation folder
        filename = f"{conversation_id}_{speaker_label}.wav"
        filepath = os.path.join(conversation_folder, filename)
        
        with open(filepath, 'wb') as f:
            f.write(audio_data.getvalue())
        
        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        
        LOGGER.info(f"Successfully saved audio file: {filepath} ({file_size_mb:.2f} MB)")
        
        # Note: Single file downloads don't get tracked in metadata
        # Only dual downloads (agent + customer) are tracked
        
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
        # Create conversation folder
        conversation_folder = os.path.join(AUDIO_STORAGE_DIR, conversation_id)
        os.makedirs(conversation_folder, exist_ok=True)
        LOGGER.info(f"Created conversation folder: {conversation_folder}")
        
        # Download agent audio
        LOGGER.info("Downloading agent audio...")
        audio_data_agent = audio_helper.download_audio(audio_url_agent)
        if audio_data_agent is None:
            LOGGER.error(f"Failed to download agent audio from URL: {audio_url_agent}")
            raise HTTPException(status_code=400, detail="Failed to download agent audio")
        
        # Save agent audio in conversation folder
        filename_agent = f"{conversation_id}_agent.wav"
        filepath_agent = os.path.join(conversation_folder, filename_agent)
        
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
                # Save customer audio in conversation folder
                filename_customer = f"{conversation_id}_customer.wav"
                filepath_customer = os.path.join(conversation_folder, filename_customer)
                
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
        
        # Track metadata in real-time if both files downloaded successfully
        if results["total_files"] == 2:
            try:
                agent_file = None
                customer_file = None
                
                for download in results["downloads"]:
                    if download["speaker"] == "agent" and download["status"] == "success":
                        agent_file = download["filepath"]
                    elif download["speaker"] == "customer" and download["status"] == "success":
                        customer_file = download["filepath"]
                
                if agent_file and customer_file:
                    metadata_entry = metadata_tracker.add_conversation(
                        conversation_id=conversation_id,
                        agent_filepath=agent_file,
                        customer_filepath=customer_file,
                        agent_url=audio_url_agent,
                        customer_url=audio_url_customer or ""
                    )
                    results["metadata_tracked"] = True
                    LOGGER.info(f"Metadata tracked for conversation {conversation_id}")
            except Exception as meta_err:
                LOGGER.error(f"Failed to track metadata: {meta_err}")
                results["metadata_tracked"] = False
        
        return JSONResponse(status_code=200, content=results)
    
    except Exception as e:
        LOGGER.error(f"Error downloading audio files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/storage/info")
def storage_info():
    """Get information about stored audio files"""
    try:
        # Count conversation folders and files
        conversation_folders = [d for d in os.listdir(AUDIO_STORAGE_DIR) 
                               if os.path.isdir(os.path.join(AUDIO_STORAGE_DIR, d))]
        
        total_files = 0
        total_size_bytes = 0
        
        for folder in conversation_folders:
            folder_path = os.path.join(AUDIO_STORAGE_DIR, folder)
            for file in os.listdir(folder_path):
                if file.endswith('.wav'):
                    total_files += 1
                    total_size_bytes += os.path.getsize(os.path.join(folder_path, file))
        
        total_size_mb = total_size_bytes / (1024 * 1024)
        
        return {
            "storage_directory": AUDIO_STORAGE_DIR,
            "total_conversations": len(conversation_folders),
            "total_files": total_files,
            "total_size_mb": round(total_size_mb, 2),
            "conversation_folders": conversation_folders[:50]  # Return first 50 folders
        }
    except Exception as e:
        LOGGER.error(f"Error getting storage info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/statistics")
def get_statistics(target_hours: Optional[float] = None):
    """
    Get comprehensive statistics about downloaded conversations
    
    Args:
        target_hours: Optional target hours to track progress against
    
    Returns:
        Statistics including total hours, conversations, storage, and progress
    """
    try:
        stats = metadata_tracker.get_statistics()
        
        response = {
            "summary": stats,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add progress tracking if target is provided
        if target_hours:
            progress_percentage = (stats['total_hours'] / target_hours) * 100 if target_hours > 0 else 0
            remaining_hours = target_hours - stats['total_hours']
            
            # Estimate conversations needed
            avg_duration_hours = stats['total_hours'] / stats['total_conversations'] if stats['total_conversations'] > 0 else 0
            estimated_conversations_needed = int(remaining_hours / avg_duration_hours) if avg_duration_hours > 0 else 0
            
            response['progress'] = {
                "target_hours": target_hours,
                "current_hours": stats['total_hours'],
                "remaining_hours": round(remaining_hours, 2),
                "progress_percentage": round(progress_percentage, 2),
                "estimated_conversations_needed": estimated_conversations_needed,
                "target_reached": stats['total_hours'] >= target_hours
            }
        
        return response
    except Exception as e:
        LOGGER.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8888"))
    LOGGER.info(f"Starting Audio Downloader API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

