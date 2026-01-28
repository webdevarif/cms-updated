import subprocess
import time

import requests

# Start server in background
server = subprocess.Popen(["python", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"])

# Wait for server to start
time.sleep(5)

# Test endpoints
try:
    # Test root
    response = requests.get("http://localhost:8000/")
    print(f"✅ Root Status Code: {response.status_code}")

    # Test schema
    response = requests.get("http://localhost:8000/api/schema/")
    print(f"✅ Schema Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✅ OpenAPI Schema is working!")
        schema = response.json()
        print(f'   Title: {schema.get("info", {}).get("title", "N/A")}')
        print(f'   Version: {schema.get("info", {}).get("version", "N/A")}')

    # Test docs
    response = requests.get("http://localhost:8000/api/docs/")
    print(f"✅ Docs Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✅ Swagger UI is working!")

except Exception as e:
    print(f"❌ Error: {e}")

# Stop server
server.terminate()
server.wait()
