"""
Storage Analyzer - Analyze downloaded audio data
Run this script hourly or on-demand to track progress
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from metadata_tracker import MetadataTracker


class StorageAnalyzer:
    """Analyze and report on downloaded audio storage"""
    
    def __init__(self, metadata_file: str = "conversations_metadata.json"):
        self.tracker = MetadataTracker(metadata_file)
        self.metadata_file = metadata_file
    
    def get_hourly_breakdown(self) -> Dict:
        """Get breakdown of downloads by hour"""
        metadata = self.tracker.get_all_metadata()
        
        hourly_data = {}
        for conv in metadata:
            timestamp = datetime.fromisoformat(conv['timestamp'])
            hour_key = timestamp.strftime("%Y-%m-%d %H:00")
            
            if hour_key not in hourly_data:
                hourly_data[hour_key] = {
                    'conversations': 0,
                    'duration_hours': 0,
                    'size_mb': 0
                }
            
            hourly_data[hour_key]['conversations'] += 1
            hourly_data[hour_key]['duration_hours'] += conv['total']['duration_hours']
            hourly_data[hour_key]['size_mb'] += conv['total']['size_mb']
        
        return hourly_data
    
    def get_progress_report(self, target_hours: float = None) -> Dict:
        """
        Get detailed progress report
        
        Args:
            target_hours: Target hours of audio to collect (optional)
        """
        stats = self.tracker.get_statistics()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": stats,
            "progress": {}
        }
        
        if target_hours:
            progress_percentage = (stats['total_hours'] / target_hours) * 100 if target_hours > 0 else 0
            remaining_hours = target_hours - stats['total_hours']
            
            # Estimate conversations needed
            avg_duration_hours = stats['total_hours'] / stats['total_conversations'] if stats['total_conversations'] > 0 else 0
            estimated_conversations_needed = int(remaining_hours / avg_duration_hours) if avg_duration_hours > 0 else 0
            
            report['progress'] = {
                "target_hours": target_hours,
                "current_hours": stats['total_hours'],
                "remaining_hours": round(remaining_hours, 2),
                "progress_percentage": round(progress_percentage, 2),
                "estimated_conversations_needed": estimated_conversations_needed,
                "target_reached": stats['total_hours'] >= target_hours
            }
        
        return report
    
    def print_detailed_report(self, target_hours: float = None):
        """Print a detailed, formatted report"""
        report = self.get_progress_report(target_hours)
        stats = report['summary']
        
        print("\n" + "=" * 70)
        print(" " * 20 + "AUDIO STORAGE ANALYSIS REPORT")
        print("=" * 70)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Summary Section
        print("\n📊 SUMMARY:")
        print(f"  Total Conversations Downloaded: {stats['total_conversations']}")
        print(f"  Total Audio Duration:           {stats['total_hours']:.2f} hours ({stats['total_minutes']:.2f} minutes)")
        print(f"  Total Storage Used:             {stats['total_size_gb']:.2f} GB ({stats['total_size_mb']:.2f} MB)")
        
        if stats['total_conversations'] > 0:
            print(f"\n📈 AVERAGES:")
            print(f"  Average Conversation Duration:  {stats['average_duration_minutes']:.2f} minutes")
            print(f"  Average Conversation Size:      {stats['average_size_mb']:.2f} MB")
        
        # Progress Section (if target is set)
        if target_hours and 'progress' in report:
            progress = report['progress']
            print(f"\n🎯 PROGRESS TO TARGET:")
            print(f"  Target Hours:                   {progress['target_hours']:.2f} hours")
            print(f"  Current Hours:                  {progress['current_hours']:.2f} hours")
            print(f"  Remaining Hours:                {progress['remaining_hours']:.2f} hours")
            print(f"  Progress:                       {progress['progress_percentage']:.1f}%")
            
            # Progress bar
            bar_length = 40
            filled = int(bar_length * progress['progress_percentage'] / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            print(f"  [{bar}] {progress['progress_percentage']:.1f}%")
            
            if progress['target_reached']:
                print(f"\n  ✅ TARGET REACHED! You can stop the download service.")
            else:
                print(f"\n  📥 Estimated conversations needed: {progress['estimated_conversations_needed']}")
        
        # Timeline Section
        if stats['total_conversations'] > 0:
            print(f"\n⏰ TIMELINE:")
            print(f"  First Download:                 {stats['first_download']}")
            print(f"  Last Download:                  {stats['last_download']}")
            
            # Calculate download rate
            first = datetime.fromisoformat(stats['first_download'])
            last = datetime.fromisoformat(stats['last_download'])
            duration = (last - first).total_seconds() / 3600  # hours
            
            if duration > 0:
                rate_conversations_per_hour = stats['total_conversations'] / duration
                rate_hours_per_hour = stats['total_hours'] / duration
                print(f"  Download Duration:              {duration:.2f} hours")
                print(f"  Download Rate:                  {rate_conversations_per_hour:.2f} conversations/hour")
                print(f"  Audio Collection Rate:          {rate_hours_per_hour:.2f} hours of audio/hour")
        
        # Storage breakdown
        print(f"\n💾 STORAGE BREAKDOWN:")
        metadata = self.tracker.get_all_metadata()
        agent_size = sum(conv['agent']['size_mb'] for conv in metadata)
        customer_size = sum(conv['customer']['size_mb'] for conv in metadata)
        print(f"  Agent Audio:                    {agent_size:.2f} MB")
        print(f"  Customer Audio:                 {customer_size:.2f} MB")
        
        print("\n" + "=" * 70)
        print()
    
    def save_report(self, filename: str = None, target_hours: float = None):
        """Save report to JSON file"""
        if filename is None:
            filename = f"storage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = self.get_progress_report(target_hours)
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✓ Report saved to {filename}")
        return filename
    
    def check_target_reached(self, target_hours: float) -> bool:
        """Check if target hours have been reached"""
        stats = self.tracker.get_statistics()
        return stats['total_hours'] >= target_hours


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze audio storage and track progress")
    parser.add_argument('--target', type=float, help='Target hours of audio to collect')
    parser.add_argument('--save', action='store_true', help='Save report to JSON file')
    parser.add_argument('--export-csv', action='store_true', help='Export metadata to CSV')
    
    args = parser.parse_args()
    
    analyzer = StorageAnalyzer()
    
    # Print detailed report
    analyzer.print_detailed_report(target_hours=args.target)
    
    # Save report if requested
    if args.save:
        analyzer.save_report(target_hours=args.target)
    
    # Export to CSV if requested
    if args.export_csv:
        analyzer.tracker.export_to_csv()
    
    # Check if target reached
    if args.target:
        if analyzer.check_target_reached(args.target):
            print(f"✅ SUCCESS! Target of {args.target} hours reached!")
            print(f"   You can now stop the download service.")
            return 0
        else:
            stats = analyzer.tracker.get_statistics()
            remaining = args.target - stats['total_hours']
            print(f"⏳ Keep downloading... {remaining:.2f} hours remaining to reach target.")
            return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

