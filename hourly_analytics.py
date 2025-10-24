#!/usr/bin/env python3
"""
Hourly Analytics Logger
Tracks URL processing statistics and saves hourly reports

Run this hourly via cron to track:
- Number of conversations processed per hour
- Success/failure/skip rates
- Storage growth
- Progress over time
"""

import os
import json
from datetime import datetime
from pathlib import Path
from direct_folder_analyzer import DirectFolderAnalyzer


ANALYTICS_DIR = "hourly_analytics"
STORAGE_PATH = "/media/vocab/e7c26124-50af-4761-94a7-61983de87073/Hrutin/downloaded_audios"


class HourlyAnalytics:
    """Track and log hourly statistics"""
    
    def __init__(self, analytics_dir: str = ANALYTICS_DIR):
        self.analytics_dir = analytics_dir
        os.makedirs(analytics_dir, exist_ok=True)
    
    def get_previous_report(self):
        """Get the most recent analytics report"""
        reports = sorted(Path(self.analytics_dir).glob("hourly_*.json"))
        
        if not reports:
            return None
        
        with open(reports[-1], 'r') as f:
            return json.load(f)
    
    def generate_report(self, storage_path: str = STORAGE_PATH, target_hours: float = None):
        """Generate hourly analytics report"""
        timestamp = datetime.now()
        report_filename = os.path.join(
            self.analytics_dir,
            f"hourly_{timestamp.strftime('%Y%m%d_%H%M')}.json"
        )
        
        # Get current statistics
        try:
            analyzer = DirectFolderAnalyzer(storage_path)
            current_stats = analyzer.analyze()
        except Exception as e:
            print(f"❌ Error analyzing storage: {e}")
            return None
        
        # Get previous report for comparison
        previous = self.get_previous_report()
        
        # Calculate changes since last report
        if previous and 'current_stats' in previous:
            prev_stats = previous['current_stats']
            new_conversations = current_stats['total_conversations'] - prev_stats.get('total_conversations', 0)
            new_hours = current_stats['total_hours'] - prev_stats.get('total_hours', 0)
            new_size_gb = current_stats['total_size_gb'] - prev_stats.get('total_size_gb', 0)
            hours_since_last = (timestamp - datetime.fromisoformat(previous['timestamp'])).total_seconds() / 3600
        else:
            new_conversations = current_stats['total_conversations']
            new_hours = current_stats['total_hours']
            new_size_gb = current_stats['total_size_gb']
            hours_since_last = 0
        
        # Build report
        report = {
            "timestamp": timestamp.isoformat(),
            "report_file": report_filename,
            "current_stats": current_stats,
            "changes_since_last": {
                "new_conversations": new_conversations,
                "new_hours": round(new_hours, 2),
                "new_size_gb": round(new_size_gb, 2),
                "hours_elapsed": round(hours_since_last, 2)
            }
        }
        
        # Add progress if target is set
        if target_hours:
            progress_pct = (current_stats['total_hours'] / target_hours * 100) if target_hours > 0 else 0
            remaining_hours = target_hours - current_stats['total_hours']
            
            report['progress'] = {
                "target_hours": target_hours,
                "current_hours": current_stats['total_hours'],
                "remaining_hours": round(remaining_hours, 2),
                "progress_percentage": round(progress_pct, 2),
                "target_reached": current_stats['total_hours'] >= target_hours
            }
        
        # Save report
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def print_report(self, report):
        """Print formatted hourly report"""
        print(f"\n{'='*70}")
        print(f"  HOURLY ANALYTICS REPORT")
        print(f"{'='*70}")
        print(f"Generated: {report['timestamp']}")
        print(f"{'='*70}\n")
        
        # Current stats
        stats = report['current_stats']
        print(f"📊 CURRENT TOTALS:")
        print(f"  Conversations:                  {stats['total_conversations']}")
        print(f"  Audio Hours:                    {stats['total_hours']:.2f} hours")
        print(f"  Storage Used:                   {stats['total_size_gb']:.2f} GB")
        print(f"  Audio Files:                    {stats['total_files']}")
        
        # Changes since last report
        changes = report['changes_since_last']
        if changes['hours_elapsed'] > 0:
            print(f"\n📈 CHANGES (Last {changes['hours_elapsed']:.1f} hours):")
            print(f"  New Conversations:              +{changes['new_conversations']}")
            print(f"  New Audio Hours:                +{changes['new_hours']:.2f} hours")
            print(f"  New Storage:                    +{changes['new_size_gb']:.2f} GB")
            
            # Calculate rate
            if changes['hours_elapsed'] > 0:
                conv_per_hour = changes['new_conversations'] / changes['hours_elapsed']
                hours_per_hour = changes['new_hours'] / changes['hours_elapsed']
                print(f"\n📊 PROCESSING RATE:")
                print(f"  Conversations/hour:             {conv_per_hour:.2f}")
                print(f"  Audio hours collected/hour:     {hours_per_hour:.2f}")
        
        # Progress
        if 'progress' in report:
            prog = report['progress']
            print(f"\n🎯 PROGRESS TO TARGET:")
            print(f"  Target:                         {prog['target_hours']:.2f} hours")
            print(f"  Current:                        {prog['current_hours']:.2f} hours")
            print(f"  Remaining:                      {prog['remaining_hours']:.2f} hours")
            print(f"  Progress:                       {prog['progress_percentage']:.1f}%")
            
            # Progress bar
            bar_length = 40
            filled = int(bar_length * prog['progress_percentage'] / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            print(f"  [{bar}] {prog['progress_percentage']:.1f}%")
            
            if prog['target_reached']:
                print(f"\n  ✅ TARGET REACHED!")
                print(f"     You can stop the download service.")
            else:
                print(f"\n  ⏳ Keep downloading...")
        
        print(f"\n{'='*70}\n")
        print(f"Report saved: {report['report_file']}")
        print(f"{'='*70}\n")
    
    def get_summary_stats(self):
        """Get summary from all hourly reports"""
        reports = sorted(Path(self.analytics_dir).glob("hourly_*.json"))
        
        if not reports:
            print("No hourly reports found yet")
            return
        
        print(f"\n{'='*70}")
        print(f"  HOURLY ANALYTICS SUMMARY")
        print(f"{'='*70}\n")
        print(f"Total Reports: {len(reports)}")
        
        # Get first and last
        with open(reports[0], 'r') as f:
            first = json.load(f)
        with open(reports[-1], 'r') as f:
            last = json.load(f)
        
        first_stats = first['current_stats']
        last_stats = last['current_stats']
        
        print(f"\n📈 OVERALL GROWTH:")
        print(f"  First Report:                   {first['timestamp']}")
        print(f"  Latest Report:                  {last['timestamp']}")
        print(f"  Conversations: {first_stats['total_conversations']} → {last_stats['total_conversations']} (+{last_stats['total_conversations'] - first_stats['total_conversations']})")
        print(f"  Hours: {first_stats['total_hours']:.2f} → {last_stats['total_hours']:.2f} (+{last_stats['total_hours'] - first_stats['total_hours']:.2f})")
        print(f"  Storage: {first_stats['total_size_gb']:.2f} GB → {last_stats['total_size_gb']:.2f} GB (+{last_stats['total_size_gb'] - first_stats['total_size_gb']:.2f} GB)")
        
        print(f"\n📊 RECENT REPORTS (Last 5):")
        for report_file in reports[-5:]:
            with open(report_file, 'r') as f:
                r = json.load(f)
            timestamp = datetime.fromisoformat(r['timestamp']).strftime('%Y-%m-%d %H:%M')
            convs = r['current_stats']['total_conversations']
            hours = r['current_stats']['total_hours']
            print(f"  {timestamp} - {convs} conversations, {hours:.2f} hours")
        
        print(f"\n{'='*70}\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate hourly analytics report',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Generate current hourly report
  python3 hourly_analytics.py
  
  # With target hours
  python3 hourly_analytics.py --target 100
  
  # Custom storage path
  python3 hourly_analytics.py --path /custom/path --target 100
  
  # View summary of all reports
  python3 hourly_analytics.py --summary
  
Add to crontab for hourly tracking:
  0 * * * * cd /path/to/AUDIO_DOWNLOADER && python3 hourly_analytics.py --target 100 >> hourly_analytics.log 2>&1
        '''
    )
    
    parser.add_argument(
        '--path',
        default=STORAGE_PATH,
        help='Path to downloaded_audios folder'
    )
    parser.add_argument(
        '--target',
        type=float,
        help='Target hours of audio to collect'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show summary of all hourly reports'
    )
    
    args = parser.parse_args()
    
    analytics = HourlyAnalytics()
    
    if args.summary:
        analytics.get_summary_stats()
    else:
        report = analytics.generate_report(args.path, args.target)
        if report:
            analytics.print_report(report)


if __name__ == "__main__":
    main()

