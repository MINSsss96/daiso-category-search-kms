import requests
import json
import time

def test_api():
    url = "http://localhost:8000/api/search"
    payload = {"query": "파란색 볼펜 어디있어?"}
    headers = {"Content-Type": "application/json"}
    
    with open("api_result.txt", "w", encoding="utf-8") as f:
        f.write(f"Testing {url}...\n")
        try:
            start_time = time.time()
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            end_time = time.time()
            
            f.write(f"Response Status: {response.status_code}\n")
            f.write(f"Time taken: {end_time - start_time:.2f}s\n")
            f.write("Response Body:\n")
            f.write(json.dumps(response.json(), indent=2, ensure_ascii=False))
            
        except requests.exceptions.Timeout:
            f.write("Error: Request timed out after 10 seconds.\n")
        except requests.exceptions.ConnectionError:
            f.write("Error: Connection refused. Is the server running?\n")
        except Exception as e:
            f.write(f"Error: {e}\n")

if __name__ == "__main__":
    test_api()
