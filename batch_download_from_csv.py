"""
Batch Audio Downloader from CSV
Reads paired_conversation_urls.csv and downloads all audio files using the FastAPI service
"""

import csv
import requests
import time
import json
from pathlib import Path
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8888"
CSV_FILE = "paired_conversation_urls.csv"
RESULTS_FILE = f"download_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
DELAY_BETWEEN_REQUESTS = 1  # seconds

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def check_server_health():
    """Check if the API server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"{Colors.OKGREEN}✓ Server is healthy and running{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.FAIL}✗ Server returned status {response.status_code}{Colors.ENDC}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"{Colors.FAIL}✗ Cannot connect to server at {BASE_URL}{Colors.ENDC}")
        print(f"  Error: {str(e)}")
        print(f"\n{Colors.WARNING}Please start the server first:{Colors.ENDC}")
        print(f"  python main.py")
        return False


def download_dual_audio(conversation_id, customer_url, agent_url):
    """
    Download both customer and agent audio files
    
    Args:
        conversation_id: Unique identifier for the conversation
        customer_url: URL for customer audio
        agent_url: URL for agent audio
    
    Returns:
        dict: Response from API
    """
    data = {
        "conversation_id": conversation_id,
        "audio_url_agent": agent_url,
        "audio_url_customer": customer_url
    }
    
    try:
        response = requests.post(f"{BASE_URL}/download/dual", data=data, timeout=120)
        return {
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "response": response.json()
        }
    except requests.exceptions.Timeout:
        return {
            "status_code": 408,
            "success": False,
            "response": {"error": "Request timeout"}
        }
    except Exception as e:
        return {
            "status_code": 500,
            "success": False,
            "response": {"error": str(e)}
        }


def read_csv_data(csv_file):
    """Read conversation data from CSV file"""
    conversations = []
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            # Skip empty rows
            if not row.get('conversation_id'):
                continue
            
            # Use the original conversation ID from CSV for naming
            conversations.append({
                "conversation_id": row['conversation_id'],  # Use original UUID
                "customer_url": row['customer_url'],
                "agent_url": row['agent_url'],
                "customer_filename": row.get('customer_filename', ''),
                "agent_filename": row.get('agent_filename', ''),
                "index": idx  # Keep index for display purposes
            })
    
    return conversations


def format_file_size(size_mb):
    """Format file size for display"""
    if size_mb < 1:
        return f"{size_mb * 1024:.1f} KB"
    return f"{size_mb:.2f} MB"


def print_download_result(conv_data, result, duration):
    """Print formatted download result"""
    conv_id = conv_data['conversation_id']
    idx = conv_data.get('index', 0)
    
    # Show index and shortened ID for readability
    display_id = f"[{idx:02d}] {conv_id[:8]}..."
    
    if result['success']:
        print(f"{Colors.OKGREEN}✓ SUCCESS:{Colors.ENDC} {display_id} (took {duration:.1f}s)")
        
        # Print details for each file
        downloads = result['response'].get('downloads', [])
        for download in downloads:
            if download['status'] == 'success':
                speaker = download['speaker']
                size = format_file_size(download['file_size_mb'])
                filename = download['filename']
                print(f"  └─ {speaker:8s} → {filename} ({size})")
            else:
                speaker = download['speaker']
                error = download.get('error', 'Unknown error')
                print(f"  {Colors.WARNING}└─ {speaker:8s} → FAILED: {error}{Colors.ENDC}")
    else:
        error_msg = result['response'].get('error', 'Unknown error')
        print(f"{Colors.FAIL}✗ FAILED:{Colors.ENDC} {display_id}")
        print(f"  └─ Error: {error_msg}")


def save_results(results, filename):
    """Save results to JSON file"""
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n{Colors.OKCYAN}Results saved to: {filename}{Colors.ENDC}")


def main():
    """Main function to process all conversations from CSV"""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=" * 70)
    print("  Batch Audio Downloader from CSV")
    print("=" * 70)
    print(f"{Colors.ENDC}")
    
    # Check if CSV file exists
    if not Path(CSV_FILE).exists():
        print(f"{Colors.FAIL}✗ CSV file not found: {CSV_FILE}{Colors.ENDC}")
        return
    
    # Check server health
    print(f"\n{Colors.BOLD}Checking server status...{Colors.ENDC}")
    if not check_server_health():
        return
    
    # Read CSV data
    print(f"\n{Colors.BOLD}Reading CSV file...{Colors.ENDC}")
    conversations = read_csv_data(CSV_FILE)
    print(f"Found {len(conversations)} conversations to process")
    
    # Process each conversation
    print(f"\n{Colors.BOLD}Starting batch download...{Colors.ENDC}\n")
    
    results = {
        "start_time": datetime.now().isoformat(),
        "csv_file": CSV_FILE,
        "total_conversations": len(conversations),
        "successful": 0,
        "failed": 0,
        "details": []
    }
    
    for idx, conv_data in enumerate(conversations, start=1):
        conv_id_short = conv_data['conversation_id'][:8]
        print(f"[{idx}/{len(conversations)}] Processing {conv_id_short}...{conv_data['conversation_id'][8:16]}...")
        
        start_time = time.time()
        result = download_dual_audio(
            conversation_id=conv_data['conversation_id'],
            customer_url=conv_data['customer_url'],
            agent_url=conv_data['agent_url']
        )
        duration = time.time() - start_time
        
        # Update statistics
        if result['success']:
            results['successful'] += 1
        else:
            results['failed'] += 1
        
        # Store detailed result
        results['details'].append({
            "conversation_id": conv_data['conversation_id'],
            "success": result['success'],
            "status_code": result['status_code'],
            "duration_seconds": round(duration, 2),
            "response": result['response']
        })
        
        # Print result
        print_download_result(conv_data, result, duration)
        print()
        
        # Delay between requests (except for last one)
        if idx < len(conversations):
            time.sleep(DELAY_BETWEEN_REQUESTS)
    
    # Print summary
    results['end_time'] = datetime.now().isoformat()
    total_duration = sum(d['duration_seconds'] for d in results['details'])
    
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"{Colors.ENDC}")
    print(f"Total conversations: {results['total_conversations']}")
    print(f"{Colors.OKGREEN}Successful:         {results['successful']}{Colors.ENDC}")
    print(f"{Colors.FAIL}Failed:             {results['failed']}{Colors.ENDC}")
    print(f"Total duration:     {total_duration:.1f}s")
    print(f"Average per conv:   {total_duration/len(conversations):.1f}s")
    
    # Save results to file
    save_results(results, RESULTS_FILE)
    
    # Show storage info
    print(f"\n{Colors.BOLD}Checking storage...{Colors.ENDC}")
    try:
        response = requests.get(f"{BASE_URL}/storage/info")
        if response.status_code == 200:
            storage = response.json()
            print(f"Total files stored: {storage['total_files']}")
            print(f"Total storage size: {format_file_size(storage['total_size_mb'])}")
    except Exception as e:
        print(f"{Colors.WARNING}Could not fetch storage info: {str(e)}{Colors.ENDC}")
    
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}✓ Batch download complete!{Colors.ENDC}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⚠ Download interrupted by user{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}✗ Unexpected error: {str(e)}{Colors.ENDC}")
        import traceback
        traceback.print_exc()

