# Simple script to test cache performance
# Run this with: python test_cache_performance.py

import requests
import time

def test_cache_performance():
    """Test how much faster cached responses are"""
    
    # The URL for our user list API
    url = "http://localhost:8000/api/users/"
    
    print("Testing cache performance...\n")
    
    # First call - this will get data from database and cache it
    print("First call (getting from database)...")
    start = time.time()
    response1 = requests.get(url)
    time1 = time.time() - start
    
    # Second call - this should get data from cache
    print("Second call (getting from cache)...")
    start = time.time()
    response2 = requests.get(url)
    time2 = time.time() - start
    
    # Print the results
    print("\n--- Results ---")
    print(f"First call time: {time1:.4f} seconds")
    print(f"Second call time: {time2:.4f} seconds")
    
    # Calculate how much faster
    if time2 > 0:
        speedup = time1 / time2
        print(f"Speedup: {speedup:.2f}x faster!")
    
    # Check if both calls returned same data
    if response1.status_code == 200 and response2.status_code == 200:
        if response1.json() == response2.json():
            print("\n✓ Both responses have the same data")
        else:
            print("\n✗ Warning: Responses are different!")
    else:
        print(f"\n✗ Error: Got status codes {response1.status_code} and {response2.status_code}")

if __name__ == "__main__":
    try:
        test_cache_performance()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
        print("Make sure Django server is running: python manage.py runserver")
    except Exception as e:
        print(f"Error: {e}")
