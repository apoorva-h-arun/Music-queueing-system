"""
Test script for Music Queue Manager API
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

def print_response(title, response):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def main():
    print("\n🎵 Music Queue Manager - API Test")
    print("="*60)
    
    # 1. Health check
    print("\n1. Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print_response("Health Check", response)
    
    # 2. Get all songs
    print("\n2. Getting all songs...")
    response = requests.get(f"{BASE_URL}/songs")
    print_response("All Songs", response)
    
    # 3. Add songs to queue
    print("\n3. Adding songs to queue...")
    for song_id in [1, 2, 3]:
        response = requests.post(f"{BASE_URL}/queue/add", json={"song_id": song_id})
        print(f"  Added song {song_id}: {response.json()['message']}")
    
    # 4. Get queue
    print("\n4. Getting current queue...")
    response = requests.get(f"{BASE_URL}/queue")
    print_response("Current Queue", response)
    
    # 5. Skip to next
    print("\n5. Skipping to next song...")
    response = requests.post(f"{BASE_URL}/queue/skip/next")
    print_response("Skip Next", response)
    
    # 6. Get queue again
    print("\n6. Queue after skip...")
    response = requests.get(f"{BASE_URL}/queue")
    print_response("Queue After Skip", response)
    
    # 7. Skip to previous
    print("\n7. Skipping to previous song...")
    response = requests.post(f"{BASE_URL}/queue/skip/prev")
    print_response("Skip Previous", response)
    
    # 8. Final queue state
    print("\n8. Final queue state...")
    response = requests.get(f"{BASE_URL}/queue")
    print_response("Final Queue", response)
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server")
        print("Make sure the server is running: python app_demo.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
