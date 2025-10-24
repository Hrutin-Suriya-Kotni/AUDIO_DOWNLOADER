#!/usr/bin/env python3
"""
Log Analyzer - Analyze processing logs to track hourly/daily activity

Parse audio_downloader.log to extract:
- How many URLs/conversations processed per hour
- Daily totals
- Processing timeline
- Success/failure rates

Usage:
    python3 log_analyzer.py --date 2025-10-23
    python3 log_analyzer.py --date 2025-10-23 --hourly
"""

import re
import argparse
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path


LOG_FILE = "/media/vocab/e7c26124-50af-4761-94a7-61983de87073/Hrutin/AUDIO_DOWNLOADER/logs/audio_downloader.log"


class LogAnalyzer:
    """Analyze audio downloader logs"""
    
    def __init__(self, log_file: str = LOG_FILE):
        self.log_file = log_file
        
        if not Path(log_file).exists():
            # Try local path as fallback
            if Path("./logs/audio_downloader.log").exists():
                self.log_file = "./logs/audio_downloader.log"
            else:
                raise FileNotFoundError(f"Log file not found: {log_file}")
    
    def parse_logs(self, target_date: str = None):
        """
        Parse log file and extract conversation processing info
        
        Args:
            target_date: Date in YYYY-MM-DD format (e.g., "2025-10-23")
        
        Returns:
            Dict with parsed data
        """
        # Pattern to match log entries
        # Example: 2025-10-17 09:10:07 - AudioDownloader - INFO - Received dual download request for conversation_id: abc123
        log_pattern = re.compile(
            r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})\s+-\s+\w+\s+-\s+\w+\s+-\s+(.*)'
        )
        
        # Pattern for conversation processing
        conv_pattern = re.compile(r'Received dual download request for conversation_id:\s+(\S+)')
        success_pattern = re.compile(r'Successfully saved (\w+) audio:.*\((\d+\.\d+)\s+MB\)')
        
        hourly_data = defaultdict(lambda: {
            'conversations': set(),
            'agent_downloads': 0,
            'customer_downloads': 0,
            'total_mb': 0
        })
        
        all_conversations = set()
        
        with open(self.log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                match = log_pattern.search(line)
                if not match:
                    continue
                
                log_date = match.group(1)
                log_time = match.group(2)
                log_message = match.group(3)
                
                # Filter by date if specified
                if target_date and log_date != target_date:
                    continue
                
                # Extract hour (e.g., "09:00")
                hour = log_time[:2] + ":00"
                hour_key = f"{log_date} {hour}"
                
                # Check for conversation processing
                conv_match = conv_pattern.search(log_message)
                if conv_match:
                    conversation_id = conv_match.group(1)
                    hourly_data[hour_key]['conversations'].add(conversation_id)
                    all_conversations.add(conversation_id)
                
                # Check for successful downloads
                success_match = success_pattern.search(log_message)
                if success_match:
                    speaker = success_match.group(1).lower()  # 'agent' or 'customer'
                    size_mb = float(success_match.group(2))
                    
                    if speaker == 'agent':
                        hourly_data[hour_key]['agent_downloads'] += 1
                    elif speaker == 'customer':
                        hourly_data[hour_key]['customer_downloads'] += 1
                    
                    hourly_data[hour_key]['total_mb'] += size_mb
        
        return {
            'hourly_data': dict(hourly_data),
            'all_conversations': all_conversations,
            'target_date': target_date
        }
    
    def print_hourly_report(self, target_date: str):
        """Print hour-by-hour breakdown for a specific date"""
        data = self.parse_logs(target_date)
        hourly = data['hourly_data']
        
        if not hourly:
            print(f"\n❌ No data found for date: {target_date}\n")
            return
        
        print(f"\n{'='*80}")
        print(f"  HOURLY PROCESSING REPORT - {target_date}")
        print(f"{'='*80}\n")
        
        # Sort by hour
        sorted_hours = sorted(hourly.keys())
        
        print(f"{'Hour':<20} {'Conversations':<15} {'Agent':<10} {'Customer':<10} {'Size (MB)':<12}")
        print(f"{'-'*80}")
        
        daily_conversations = set()
        daily_agent = 0
        daily_customer = 0
        daily_size = 0
        
        for hour_key in sorted_hours:
            hour = hour_key.split()[1]  # Get just the time part
            h_data = hourly[hour_key]
            
            num_convs = len(h_data['conversations'])
            agent_count = h_data['agent_downloads']
            customer_count = h_data['customer_downloads']
            size_mb = h_data['total_mb']
            
            print(f"{hour:<20} {num_convs:<15} {agent_count:<10} {customer_count:<10} {size_mb:<12.2f}")
            
            # Add to daily totals
            daily_conversations.update(h_data['conversations'])
            daily_agent += agent_count
            daily_customer += customer_count
            daily_size += size_mb
        
        print(f"{'-'*80}")
        print(f"{'DAILY TOTAL':<20} {len(daily_conversations):<15} {daily_agent:<10} {daily_customer:<10} {daily_size:<12.2f}")
        print(f"\n{'='*80}")
        
        # Summary
        print(f"\n📊 SUMMARY FOR {target_date}:")
        print(f"  Total Conversations Processed:  {len(daily_conversations)}")
        print(f"  Total Agent Downloads:          {daily_agent}")
        print(f"  Total Customer Downloads:       {daily_customer}")
        print(f"  Total Data Downloaded:          {daily_size / 1024:.2f} GB ({daily_size:.2f} MB)")
        print(f"  Complete Pairs (both files):    {min(daily_agent, daily_customer)}")
        
        if daily_agent != daily_customer:
            diff = abs(daily_agent - daily_customer)
            print(f"  ⚠️  Incomplete Downloads:         {diff} (agent/customer mismatch)")
        
        print(f"\n{'='*80}\n")
    
    def print_daily_summary(self, start_date: str = None, end_date: str = None):
        """Print daily summary across date range"""
        data = self.parse_logs()
        hourly = data['hourly_data']
        
        if not hourly:
            print(f"\n❌ No data found in logs\n")
            return
        
        # Group by date
        daily_data = defaultdict(lambda: {
            'conversations': set(),
            'agent_downloads': 0,
            'customer_downloads': 0,
            'total_mb': 0
        })
        
        for hour_key, h_data in hourly.items():
            date = hour_key.split()[0]  # Get date part
            
            daily_data[date]['conversations'].update(h_data['conversations'])
            daily_data[date]['agent_downloads'] += h_data['agent_downloads']
            daily_data[date]['customer_downloads'] += h_data['customer_downloads']
            daily_data[date]['total_mb'] += h_data['total_mb']
        
        print(f"\n{'='*80}")
        print(f"  DAILY PROCESSING SUMMARY")
        print(f"{'='*80}\n")
        
        print(f"{'Date':<15} {'Conversations':<15} {'Agent':<10} {'Customer':<10} {'Size (GB)':<12}")
        print(f"{'-'*80}")
        
        for date in sorted(daily_data.keys()):
            d_data = daily_data[date]
            num_convs = len(d_data['conversations'])
            agent_count = d_data['agent_downloads']
            customer_count = d_data['customer_downloads']
            size_gb = d_data['total_mb'] / 1024
            
            print(f"{date:<15} {num_convs:<15} {agent_count:<10} {customer_count:<10} {size_gb:<12.2f}")
        
        print(f"{'-'*80}")
        
        # Grand total
        all_convs = set()
        total_agent = 0
        total_customer = 0
        total_size = 0
        
        for d_data in daily_data.values():
            all_convs.update(d_data['conversations'])
            total_agent += d_data['agent_downloads']
            total_customer += d_data['customer_downloads']
            total_size += d_data['total_mb']
        
        print(f"{'GRAND TOTAL':<15} {len(all_convs):<15} {total_agent:<10} {total_customer:<10} {total_size/1024:<12.2f}")
        print(f"\n{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze audio downloader logs for processing statistics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Hourly breakdown for specific date
  python3 log_analyzer.py --date 2025-10-23
  
  # Daily summary across all dates
  python3 log_analyzer.py --summary
  
  # Use custom log file
  python3 log_analyzer.py --date 2025-10-23 --log ./logs/audio_downloader.log
        '''
    )
    
    parser.add_argument(
        '--date',
        help='Target date in YYYY-MM-DD format (e.g., 2025-10-23)'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show daily summary across all dates'
    )
    parser.add_argument(
        '--log',
        default=LOG_FILE,
        help='Path to log file'
    )
    
    args = parser.parse_args()
    
    try:
        analyzer = LogAnalyzer(args.log)
        
        if args.summary:
            analyzer.print_daily_summary()
        elif args.date:
            analyzer.print_hourly_report(args.date)
        else:
            # Default: show summary
            analyzer.print_daily_summary()
    
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}\n")
        print("Make sure the log file exists at:")
        print(f"  {LOG_FILE}")
        print("\nOr specify a custom path with --log option\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

