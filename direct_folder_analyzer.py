#!/usr/bin/env python3
"""
Direct Folder Analyzer - Analyze audio files directly from disk
Scans the actual storage folder and calculates statistics from audio files
"""

import os
import sys
from pathlib import Path
from pydub import AudioSegment
from datetime import datetime
import argparse


class DirectFolderAnalyzer:
    """Analyze audio storage folder directly"""
    
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        
        if not os.path.exists(storage_path):
            raise FileNotFoundError(f"Storage path does not exist: {storage_path}")
    
    def analyze(self):
        """Scan folder and analyze all audio files"""
        print(f"\n{'='*70}")
        print(f"  DIRECT FOLDER ANALYSIS")
        print(f"{'='*70}")
        print(f"Scanning: {self.storage_path}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        # Scan all conversation folders
        conversation_folders = [
            d for d in os.listdir(self.storage_path)
            if os.path.isdir(os.path.join(self.storage_path, d))
        ]
        
        if not conversation_folders:
            print("⚠️  No conversation folders found!")
            return {
                'total_conversations': 0,
                'total_files': 0,
                'total_hours': 0,
                'total_minutes': 0,
                'total_size_gb': 0,
                'total_size_mb': 0,
                'average_duration_min': 0,
                'average_size_mb': 0,
                'incomplete_conversations': 0
            }
        
        print(f"Found {len(conversation_folders)} conversation folders")
        print(f"Analyzing audio files...\n")
        
        # Statistics
        total_conversations = 0
        total_files = 0
        total_size_bytes = 0
        total_duration_seconds = 0
        conversations_data = []
        
        # Analyze each conversation
        for idx, folder_name in enumerate(sorted(conversation_folders), start=1):
            folder_path = os.path.join(self.storage_path, folder_name)
            
            # Find audio files in this conversation
            audio_files = [
                f for f in os.listdir(folder_path)
                if f.endswith('.wav')
            ]
            
            if not audio_files:
                print(f"  [{idx}] {folder_name[:40]:<40} - No audio files")
                continue
            
            # Analyze files in this conversation
            conv_size = 0
            conv_duration = 0
            agent_file = None
            customer_file = None
            
            for audio_file in audio_files:
                file_path = os.path.join(folder_path, audio_file)
                file_size = os.path.getsize(file_path)
                conv_size += file_size
                
                # Get duration with robust error handling
                try:
                    if file_size == 0:
                        continue
                    
                    audio = AudioSegment.from_wav(file_path)
                    duration_sec = len(audio) / 1000.0
                    
                    if duration_sec <= 0:
                        continue
                    
                    if duration_sec > conv_duration:
                        conv_duration = duration_sec
                    
                    if 'agent' in audio_file.lower():
                        agent_file = True
                    elif 'customer' in audio_file.lower():
                        customer_file = True
                        
                except Exception as e:
                    pass  # Skip files with errors
            
            # Update totals
            total_conversations += 1
            total_files += len(audio_files)
            total_size_bytes += conv_size
            total_duration_seconds += conv_duration
            
            # Store conversation data
            conversations_data.append({
                'folder': folder_name,
                'files': len(audio_files),
                'size_mb': conv_size / (1024 * 1024),
                'duration_min': conv_duration / 60,
                'has_agent': agent_file is not None,
                'has_customer': customer_file is not None
            })
            
            # Show progress every 50 conversations
            if idx % 50 == 0:
                print(f"  Processed {idx}/{len(conversation_folders)} conversations...")
        
        # Calculate final statistics
        total_size_mb = total_size_bytes / (1024 * 1024)
        total_size_gb = total_size_mb / 1024
        total_duration_min = total_duration_seconds / 60
        total_duration_hours = total_duration_min / 60
        
        avg_duration_min = total_duration_min / total_conversations if total_conversations > 0 else 0
        avg_size_mb = total_size_mb / total_conversations if total_conversations > 0 else 0
        
        # Print results
        print(f"\n{'='*70}")
        print(f"  ANALYSIS RESULTS")
        print(f"{'='*70}\n")
        
        print(f"📊 CONVERSATIONS:")
        print(f"  Total Conversations:            {total_conversations}")
        print(f"  Total Audio Files:              {total_files}")
        
        print(f"\n⏱️  DURATION:")
        print(f"  Total Hours:                    {total_duration_hours:.2f} hours")
        print(f"  Total Minutes:                  {total_duration_min:.2f} minutes")
        print(f"  Average per Conversation:       {avg_duration_min:.2f} minutes")
        
        print(f"\n💾 STORAGE:")
        print(f"  Total Size:                     {total_size_gb:.2f} GB")
        print(f"  Total Size:                     {total_size_mb:.2f} MB")
        print(f"  Average per Conversation:       {avg_size_mb:.2f} MB")
        
        # Check for incomplete conversations
        incomplete = [c for c in conversations_data if not (c['has_agent'] and c['has_customer'])]
        if incomplete:
            print(f"\n⚠️  INCOMPLETE CONVERSATIONS: {len(incomplete)}")
        
        print(f"\n{'='*70}\n")
        
        return {
            'total_conversations': total_conversations,
            'total_files': total_files,
            'total_hours': round(total_duration_hours, 2),
            'total_minutes': round(total_duration_min, 2),
            'total_size_gb': round(total_size_gb, 2),
            'total_size_mb': round(total_size_mb, 2),
            'average_duration_min': round(avg_duration_min, 2),
            'average_size_mb': round(avg_size_mb, 2),
            'incomplete_conversations': len(incomplete)
        }


def main():
    parser = argparse.ArgumentParser(description='Analyze audio storage folder directly')
    
    parser.add_argument(
        '--path',
        default='/media/vocab/e7c26124-50af-4761-94a7-61983de87073/Hrutin/downloaded_audios',
        help='Path to downloaded_audios folder'
    )
    parser.add_argument(
        '--target',
        type=float,
        help='Target hours (shows progress)'
    )
    
    args = parser.parse_args()
    
    try:
        analyzer = DirectFolderAnalyzer(args.path)
        stats = analyzer.analyze()
        
        if args.target and stats:
            current_hours = stats['total_hours']
            remaining = args.target - current_hours
            progress_pct = (current_hours / args.target * 100) if args.target > 0 else 0
            
            print(f"🎯 PROGRESS TO TARGET:")
            print(f"  Target: {args.target:.2f} hours")
            print(f"  Current: {current_hours:.2f} hours")
            print(f"  Remaining: {remaining:.2f} hours")
            print(f"  Progress: {progress_pct:.1f}%")
            
            bar_length = 40
            filled = int(bar_length * progress_pct / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            print(f"  [{bar}] {progress_pct:.1f}%")
            
            if current_hours >= args.target:
                print(f"\n  ✅ TARGET REACHED!")
            print(f"\n{'='*70}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

