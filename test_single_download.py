"""
Test Single Download
Quick test script to download one conversation from the CSV
"""

import csv
import requests
import json

BASE_URL = "http://localhost:8888"
CSV_FILE = "paired_conversation_urls.csv"

def test_single():
    """Test downloading the first conversation from CSV"""
    
    # Read first conversation from CSV
    with open(CSV_FILE, 'r') as f:
        reader = csv.DictReader(f)
        first_row = next(reader)
    
    print("=" * 60)
    print("Testing Single Audio Download")
    print("=" * 60)
    
    print("\nConversation ID:", first_row['conversation_id'])
    print("Customer URL:", first_row['customer_url'][:60] + "...")
    print("Agent URL:", first_row['agent_url'][:60] + "...")
    
    # Use the original conversation ID from CSV
    conv_id = first_row['conversation_id']
    print(f"\nUsing conversation ID: {conv_id}")
    
    # Check server health
    print("\n1. Checking server health...")
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        if health.status_code == 200:
            print("   ✓ Server is running")
        else:
            print(f"   ✗ Server returned status {health.status_code}")
            return
    except Exception as e:
        print(f"   ✗ Cannot connect to server: {str(e)}")
        print("\n   Please start the server first:")
        print("   python main.py")
        return
    
    # Download dual audio
    print("\n2. Downloading audio files...")
    data = {
        "conversation_id": conv_id,
        "audio_url_agent": first_row['agent_url'],
        "audio_url_customer": first_row['customer_url']
    }
    
    try:
        response = requests.post(f"{BASE_URL}/download/dual", data=data, timeout=120)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n   ✓ Download successful!")
            print("\n   Response:")
            print(json.dumps(result, indent=4))
            
            # Check storage
            print("\n3. Checking storage...")
            storage = requests.get(f"{BASE_URL}/storage/info")
            if storage.status_code == 200:
                storage_data = storage.json()
                print(f"   Total files: {storage_data['total_files']}")
                print(f"   Total size: {storage_data['total_size_mb']} MB")
                print(f"   Recent files: {storage_data['files'][:5]}")
        else:
            print(f"\n   ✗ Download failed!")
            print(f"   Response: {response.text}")
    
    except requests.exceptions.Timeout:
        print("   ✗ Request timed out (this can happen with large files)")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    test_single()

