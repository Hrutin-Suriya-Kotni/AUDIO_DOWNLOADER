"""
Metadata Tracker - Track all downloaded conversations with full metadata
Appends data in real-time as conversations are downloaded
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from pydub import AudioSegment

METADATA_FILE = "conversations_metadata.json"


class MetadataTracker:
    """Track and persist metadata for all downloaded conversations"""
    
    def __init__(self, metadata_file: str = METADATA_FILE):
        self.metadata_file = metadata_file
        self._ensure_metadata_file()
    
    def _ensure_metadata_file(self):
        """Ensure metadata file exists, create if not"""
        if not os.path.exists(self.metadata_file):
            self._save_metadata([])
    
    def _load_metadata(self) -> List[Dict]:
        """Load existing metadata from file"""
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_metadata(self, metadata: List[Dict]):
        """Save metadata to file"""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def conversation_exists(self, conversation_id: str) -> bool:
        """Check if conversation already exists in metadata"""
        metadata = self._load_metadata()
        return any(conv['conversation_id'] == conversation_id for conv in metadata)
    
    def get_audio_duration(self, audio_path: str) -> float:
        """Get audio duration in seconds"""
        try:
            audio = AudioSegment.from_wav(audio_path)
            return len(audio) / 1000.0  # Convert ms to seconds
        except Exception as e:
            print(f"Error getting duration for {audio_path}: {e}")
            return 0.0
    
    def add_conversation(
        self,
        conversation_id: str,
        agent_filepath: str,
        customer_filepath: str,
        agent_url: str = "",
        customer_url: str = ""
    ) -> Dict:
        """
        Add conversation metadata and append to file in real-time
        
        Args:
            conversation_id: Unique conversation identifier
            agent_filepath: Path to agent audio file
            customer_filepath: Path to customer audio file
            agent_url: Original URL for agent audio
            customer_url: Original URL for customer audio
        
        Returns:
            Dict with conversation metadata
        """
        # Check if already exists
        if self.conversation_exists(conversation_id):
            print(f"⚠ Conversation {conversation_id} already exists in metadata")
            return {}
        
        # Get file information
        agent_size_mb = os.path.getsize(agent_filepath) / (1024 * 1024) if os.path.exists(agent_filepath) else 0
        customer_size_mb = os.path.getsize(customer_filepath) / (1024 * 1024) if os.path.exists(customer_filepath) else 0
        
        # Get audio durations
        agent_duration_sec = self.get_audio_duration(agent_filepath) if os.path.exists(agent_filepath) else 0
        customer_duration_sec = self.get_audio_duration(customer_filepath) if os.path.exists(customer_filepath) else 0
        
        # Calculate total duration (assuming both are same length for dual channel)
        total_duration_sec = max(agent_duration_sec, customer_duration_sec)
        total_duration_min = total_duration_sec / 60
        total_duration_hours = total_duration_min / 60
        
        # Create metadata entry
        metadata_entry = {
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "agent": {
                "filepath": agent_filepath,
                "url": agent_url,
                "size_mb": round(agent_size_mb, 2),
                "duration_seconds": round(agent_duration_sec, 2),
                "duration_minutes": round(agent_duration_sec / 60, 2),
                "exists": os.path.exists(agent_filepath)
            },
            "customer": {
                "filepath": customer_filepath,
                "url": customer_url,
                "size_mb": round(customer_size_mb, 2),
                "duration_seconds": round(customer_duration_sec, 2),
                "duration_minutes": round(customer_duration_sec / 60, 2),
                "exists": os.path.exists(customer_filepath)
            },
            "total": {
                "size_mb": round(agent_size_mb + customer_size_mb, 2),
                "duration_seconds": round(total_duration_sec, 2),
                "duration_minutes": round(total_duration_min, 2),
                "duration_hours": round(total_duration_hours, 4)
            }
        }
        
        # Load existing metadata
        all_metadata = self._load_metadata()
        
        # Append new entry
        all_metadata.append(metadata_entry)
        
        # Save immediately (real-time append)
        self._save_metadata(all_metadata)
        
        print(f"✓ Metadata saved for {conversation_id} ({total_duration_min:.2f} min)")
        
        return metadata_entry
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics about all downloaded conversations"""
        metadata = self._load_metadata()
        
        if not metadata:
            return {
                "total_conversations": 0,
                "total_hours": 0,
                "total_minutes": 0,
                "total_size_mb": 0,
                "total_size_gb": 0
            }
        
        total_conversations = len(metadata)
        total_hours = sum(conv['total']['duration_hours'] for conv in metadata)
        total_minutes = sum(conv['total']['duration_minutes'] for conv in metadata)
        total_size_mb = sum(conv['total']['size_mb'] for conv in metadata)
        total_size_gb = total_size_mb / 1024
        
        # Calculate averages
        avg_duration_minutes = total_minutes / total_conversations if total_conversations > 0 else 0
        avg_size_mb = total_size_mb / total_conversations if total_conversations > 0 else 0
        
        return {
            "total_conversations": total_conversations,
            "total_hours": round(total_hours, 2),
            "total_minutes": round(total_minutes, 2),
            "total_seconds": round(total_minutes * 60, 2),
            "total_size_mb": round(total_size_mb, 2),
            "total_size_gb": round(total_size_gb, 2),
            "average_duration_minutes": round(avg_duration_minutes, 2),
            "average_size_mb": round(avg_size_mb, 2),
            "first_download": metadata[0]['timestamp'] if metadata else None,
            "last_download": metadata[-1]['timestamp'] if metadata else None
        }
    
    def get_all_metadata(self) -> List[Dict]:
        """Get all conversation metadata"""
        return self._load_metadata()
    
    def export_to_csv(self, output_file: str = "conversations_metadata.csv"):
        """Export metadata to CSV format"""
        import csv
        
        metadata = self._load_metadata()
        if not metadata:
            print("No metadata to export")
            return
        
        with open(output_file, 'w', newline='') as f:
            fieldnames = [
                'conversation_id', 'timestamp',
                'agent_filepath', 'agent_size_mb', 'agent_duration_min',
                'customer_filepath', 'customer_size_mb', 'customer_duration_min',
                'total_size_mb', 'total_duration_hours'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for conv in metadata:
                writer.writerow({
                    'conversation_id': conv['conversation_id'],
                    'timestamp': conv['timestamp'],
                    'agent_filepath': conv['agent']['filepath'],
                    'agent_size_mb': conv['agent']['size_mb'],
                    'agent_duration_min': conv['agent']['duration_minutes'],
                    'customer_filepath': conv['customer']['filepath'],
                    'customer_size_mb': conv['customer']['size_mb'],
                    'customer_duration_min': conv['customer']['duration_minutes'],
                    'total_size_mb': conv['total']['size_mb'],
                    'total_duration_hours': conv['total']['duration_hours']
                })
        
        print(f"✓ Metadata exported to {output_file}")


if __name__ == "__main__":
    # Example usage
    tracker = MetadataTracker()
    stats = tracker.get_statistics()
    
    print("\n" + "=" * 60)
    print("METADATA TRACKER - CURRENT STATISTICS")
    print("=" * 60)
    print(f"Total Conversations: {stats['total_conversations']}")
    print(f"Total Hours: {stats['total_hours']:.2f} hours")
    print(f"Total Minutes: {stats['total_minutes']:.2f} minutes")
    print(f"Total Storage: {stats['total_size_gb']:.2f} GB ({stats['total_size_mb']:.2f} MB)")
    
    if stats['total_conversations'] > 0:
        print(f"\nAverage per conversation:")
        print(f"  Duration: {stats['average_duration_minutes']:.2f} minutes")
        print(f"  Size: {stats['average_size_mb']:.2f} MB")
        print(f"\nFirst download: {stats['first_download']}")
        print(f"Last download: {stats['last_download']}")
    print("=" * 60 + "\n")

