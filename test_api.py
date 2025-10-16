"""
Test script for Audio Downloader API
Run this after starting the main.py server
"""

import requests
import json

BASE_URL = "http://localhost:8001"


def test_health():
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_root():
    """Test root endpoint"""
    print("\n=== Testing Root Endpoint ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_single_download():
    """Test single audio download"""
    print("\n=== Testing Single Audio Download ===")
    
    # Replace with actual audio URL for testing
    data = {
        "conversation_id": "test_conv_001",
        "audio_url": "https://example.com/sample_audio.mp3",
        "speaker_label": "agent"
    }
    
    response = requests.post(f"{BASE_URL}/download/single", data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code in [200, 400]  # 400 expected if URL is invalid


def test_dual_download():
    """Test dual audio download"""
    print("\n=== Testing Dual Audio Download ===")
    
    # Replace with actual audio URLs for testing
    data = {
        "conversation_id": "test_conv_002",
        "audio_url_agent": "https://example.com/agent_audio.mp3",
        "audio_url_customer": "https://example.com/customer_audio.mp3"
    }
    
    response = requests.post(f"{BASE_URL}/download/dual", data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code in [200, 400]  # 400 expected if URLs are invalid


def test_storage_info():
    """Test storage info endpoint"""
    print("\n=== Testing Storage Info ===")
    response = requests.get(f"{BASE_URL}/storage/info")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Audio Downloader API Test Suite")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Storage Info", test_storage_info),
        ("Single Download", test_single_download),
        ("Dual Download", test_dual_download),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, "PASSED" if passed else "FAILED"))
        except Exception as e:
            print(f"ERROR: {str(e)}")
            results.append((test_name, "ERROR"))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    for test_name, result in results:
        print(f"{test_name:.<50} {result}")
    print("=" * 60)


if __name__ == "__main__":
    print("Make sure the server is running at http://localhost:8001")
    print("Start server with: python main.py")
    input("\nPress Enter to start tests...")
    
    run_all_tests()

