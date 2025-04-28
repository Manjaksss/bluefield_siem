import requests
import random
import time

# If running locally
url = "http://127.0.0.1:8000/event"

# If on Render (use your deployed URL):
# url = "https://yourrenderapp.onrender.com/event"

router_names = ["GaltonRUT956", "NewtonRUT240", "TeslaRUT360"]
event_types = ["Login Success", "Login Failure", "SSH Intrusion", "Web Login", "Port Scan"]
descriptions = [
    "Successful web admin login",
    "Failed web login attempt",
    "SSH brute force detected",
    "Web interface accessed",
    "Port scan detected on WAN interface"
]

for i in range(23):
    payload = {
        "router_name": random.choice(router_names),
        "source_ip": f"192.168.1.{random.randint(1, 254)}",
        "event_type": random.choice(event_types),
        "description": random.choice(descriptions),
    }
    response = requests.post(url, json=payload)
    print(f"Event {i+1}: {response.status_code} {response.json()}")
    time.sleep(1)  # Wait 1 second between sends
