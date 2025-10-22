#!/usr/bin/env python3
"""
Direct Folder Analyzer - Analyze audio files directly from disk
Scans the actual storage folder and calculates statistics from audio files

No dependency on metadata JSON - reads directly from filesystem!
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
            return
        
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
                
                # Get duration
                try:
                    audio = AudioSegment.from_wav(file_path)
                    duration_sec = len(audio) / 1000.0
                    
                    # Use max duration (both should be same for dual channel)
                    if duration_sec > conv_duration:
                        conv_duration = duration_sec
                    
                    # Identify agent/customer
                    if 'agent' in audio_file.lower():
                        agent_file = True
                    elif 'customer' in audio_file.lower():
                        customer_file = True
                        
                except Exception as e:
                    print(f"    ⚠️  Error reading {audio_file}: {e}")
            
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
            
            # Show progress every 10 conversations
            if idx % 10 == 0:
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
        print(f"  Total Seconds:                  {total_duration_seconds:.2f} seconds")
        print(f"  Average per Conversation:       {avg_duration_min:.2f} minutes")
        
        print(f"\n💾 STORAGE:")
        print(f"  Total Size:                     {total_size_gb:.2f} GB")
        print(f"  Total Size:                     {total_size_mb:.2f} MB")
        print(f"  Average per Conversation:       {avg_size_mb:.2f} MB")
        
        # Check for incomplete conversations (missing agent or customer)
        incomplete = [c for c in conversations_data if not (c['has_agent'] and c['has_customer'])]
        if incomplete:
            print(f"\n⚠️  INCOMPLETE CONVERSATIONS: {len(incomplete)}")
            for conv in incomplete[:5]:
                status = []
                if not conv['has_agent']:
                    status.append('missing agent')
                if not conv['has_customer']:
                    status.append('missing customer')
                print(f"    - {conv['folder'][:50]}: {', '.join(status)}")
            if len(incomplete) > 5:
                print(f"    ... and {len(incomplete) - 5} more")
        
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
    
    def analyze_with_target(self, target_hours: float):
        """Analyze and show progress toward target"""
        stats = self.analyze()
        
        current_hours = stats['total_hours']
        remaining_hours = target_hours - current_hours
        progress_pct = (current_hours / target_hours * 100) if target_hours > 0 else 0
        
        # Estimate conversations needed
        avg_hours_per_conv = current_hours / stats['total_conversations'] if stats['total_conversations'] > 0 else 0
        estimated_needed = int(remaining_hours / avg_hours_per_conv) if avg_hours_per_conv > 0 else 0
        
        print(f"🎯 PROGRESS TO TARGET:")
        print(f"  Target Hours:                   {target_hours:.2f} hours")
        print(f"  Current Hours:                  {current_hours:.2f} hours")
        print(f"  Remaining Hours:                {remaining_hours:.2f} hours")
        print(f"  Progress:                       {progress_pct:.1f}%")
        
        # Progress bar
        bar_length = 40
        filled = int(bar_length * progress_pct / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"  [{bar}] {progress_pct:.1f}%")
        
        if current_hours >= target_hours:
            print(f"\n  ✅ TARGET REACHED! You have {current_hours:.2f} hours!")
            print(f"     You can stop downloading now.")
        else:
            print(f"\n  📥 Estimated conversations needed: ~{estimated_needed}")
            print(f"     Keep downloading to reach {target_hours} hours target")
        
        print(f"\n{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze audio storage folder directly from disk',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Analyze default location
  python3 direct_folder_analyzer.py
  
  # Analyze custom location
  python3 direct_folder_analyzer.py --path /path/to/downloaded_audios
  
  # With target hours
  python3 direct_folder_analyzer.py --target 100
  
  # Custom path with target
  python3 direct_folder_analyzer.py --path /media/vocab/.../downloaded_audios --target 100
        '''
    )
    
    parser.add_argument(
        '--path',
        default='/media/vocab/e7c26124-50af-4761-94a7-61983de87073/Hrutin/downloaded_audios',
        help='Path to downloaded_audios folder (default: server path)'
    )
    parser.add_argument(
        '--target',
        type=float,
        help='Target hours of audio to collect'
    )
    
    args = parser.parse_args()
    
    try:
        analyzer = DirectFolderAnalyzer(args.path)
        
        if args.target:
            analyzer.analyze_with_target(args.target)
        else:
            analyzer.analyze()
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {str(e)}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

