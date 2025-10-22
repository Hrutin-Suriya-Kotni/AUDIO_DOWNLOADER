#!/usr/bin/env python3
"""
Simple Audio Uploader Client
Upload audio files from CSV to remote server - No hassle!

Usage:
    python3 client_uploader.py --csv your_file.csv
"""

import csv
import requests
import argparse
import time
from datetime import datetime
from pathlib import Path


# Server Configuration
SERVER_URL = "http://27.111.72.52:8888"
UPLOAD_ENDPOINT = f"{SERVER_URL}/download/dual"


class Colors:
    """Simple color codes for terminal"""
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header():
    """Print welcome header"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print(f"  Audio Uploader - Send Files to Server")
    print(f"{'='*60}{Colors.RESET}\n")
    print(f"Server: {Colors.BLUE}{SERVER_URL}{Colors.RESET}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


def check_server():
    """Check if server is accessible"""
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"{Colors.GREEN}✓ Server is online and ready{Colors.RESET}\n")
            return True
        else:
            print(f"{Colors.RED}✗ Server returned error: {response.status_code}{Colors.RESET}")
            return False
    except Exception as e:
        print(f"{Colors.RED}✗ Cannot connect to server: {str(e)}{Colors.RESET}")
        print(f"{Colors.YELLOW}Please check your internet connection{Colors.RESET}")
        return False


def read_csv(csv_file):
    """Read conversations from CSV file"""
    conversations = []
    
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('conversation_id'):
                    conversations.append({
                        'conversation_id': row['conversation_id'].strip(),
                        'agent_url': row.get('agent_url', '').strip(),
                        'customer_url': row.get('customer_url', '').strip()
                    })
        
        if not conversations:
            print(f"{Colors.RED}✗ No valid conversations found in CSV{Colors.RESET}")
            return None
        
        print(f"{Colors.GREEN}✓ Found {len(conversations)} conversations to upload{Colors.RESET}\n")
        return conversations
    
    except FileNotFoundError:
        print(f"{Colors.RED}✗ CSV file not found: {csv_file}{Colors.RESET}")
        return None
    except Exception as e:
        print(f"{Colors.RED}✗ Error reading CSV: {str(e)}{Colors.RESET}")
        return None


def upload_conversation(conv_data, index, total):
    """Upload a single conversation to server"""
    conv_id = conv_data['conversation_id']
    
    # Show progress
    print(f"{Colors.BOLD}[{index}/{total}]{Colors.RESET} Processing: {Colors.BLUE}{conv_id[:30]}...{Colors.RESET}")
    
    # Prepare data
    data = {
        'conversation_id': conv_data['conversation_id'],
        'audio_url_agent': conv_data['agent_url'],
        'audio_url_customer': conv_data['customer_url']
    }
    
    try:
        # Send to server
        start_time = time.time()
        response = requests.post(UPLOAD_ENDPOINT, data=data, timeout=300)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            # Check if it was skipped (already exists)
            if result.get('status') == 'skipped':
                print(f"  {Colors.YELLOW}⊘ Skipped:{Colors.RESET} {result.get('message', 'Already exists')}")
                print(f"    Reason: This conversation_id already exists on server")
                print()
                return 'skipped'
            
            # Regular success
            total_files = result.get('total_files', 0)
            
            # Show success
            print(f"  {Colors.GREEN}✓ Success!{Colors.RESET} Uploaded {total_files} files in {duration:.1f}s")
            
            # Show file details
            for download in result.get('downloads', []):
                if download['status'] == 'success':
                    speaker = download['speaker']
                    size = download['file_size_mb']
                    print(f"    → {speaker}: {size} MB")
            
            print()  # Empty line for spacing
            return True
        else:
            print(f"  {Colors.RED}✗ Failed:{Colors.RESET} Server error {response.status_code}")
            print()
            return False
    
    except requests.exceptions.Timeout:
        print(f"  {Colors.YELLOW}⚠ Timeout:{Colors.RESET} Upload took too long (>5 min)")
        print()
        return False
    except Exception as e:
        print(f"  {Colors.RED}✗ Error:{Colors.RESET} {str(e)}")
        print()
        return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Upload audio files from CSV to server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python3 client_uploader.py --csv conversations.csv
  python3 client_uploader.py --csv /path/to/data.csv
  
CSV Format:
  conversation_id,agent_url,customer_url
  conv_001,https://...,https://...
        '''
    )
    parser.add_argument('--csv', required=True, help='Path to CSV file with conversations')
    
    args = parser.parse_args()
    
    # Print header
    print_header()
    
    # Check server
    if not check_server():
        print(f"\n{Colors.RED}Cannot proceed without server connection. Exiting.{Colors.RESET}\n")
        return
    
    # Read CSV
    conversations = read_csv(args.csv)
    if not conversations:
        return
    
    # Upload all conversations
    print(f"{Colors.BOLD}Starting upload...{Colors.RESET}\n")
    
    successful = 0
    failed = 0
    skipped = 0
    start_time = time.time()
    
    for idx, conv in enumerate(conversations, start=1):
        result = upload_conversation(conv, idx, len(conversations))
        if result == True:
            successful += 1
        elif result == 'skipped':
            skipped += 1
        else:
            failed += 1
        
        # Small delay between uploads
        if idx < len(conversations):
            time.sleep(1)
    
    # Print summary
    total_duration = time.time() - start_time
    
    print(f"{Colors.BOLD}{'='*60}")
    print(f"  Upload Complete!")
    print(f"{'='*60}{Colors.RESET}\n")
    print(f"Total conversations: {len(conversations)}")
    print(f"{Colors.GREEN}Successful: {successful}{Colors.RESET}")
    if skipped > 0:
        print(f"{Colors.YELLOW}Skipped (duplicates): {skipped}{Colors.RESET}")
    if failed > 0:
        print(f"{Colors.RED}Failed: {failed}{Colors.RESET}")
    print(f"Total time: {total_duration:.1f}s")
    if successful > 0:
        print(f"Average: {total_duration/successful:.1f}s per conversation\n")
    else:
        print()
    
    # Show next steps
    print(f"{Colors.BLUE}Check server status:{Colors.RESET}")
    print(f"  curl {SERVER_URL}/statistics?target_hours=100")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠ Upload interrupted by user{Colors.RESET}\n")
    except Exception as e:
        print(f"\n{Colors.RED}✗ Unexpected error: {str(e)}{Colors.RESET}\n")

