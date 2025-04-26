
# Bluefield SIEM (Updated for Python 3.13)

## Local Development

1. Install dependencies:

    .\venv\Scripts\python.exe -m pip install -r requirements.txt

2. Run the app:

    .\venv\Scripts\python.exe -m uvicorn app.main:app --reload

Access on: http://localhost:8000

## Deploy to Render.com

1. Create GitHub repo and push the code.
2. Connect Render.com to GitHub.
3. Set environment variables:
   - SECRET_KEY
   - ADMIN_USERNAME
   - ADMIN_PASSWORD
4. Deploy!

POST events to:

    POST https://your-app-url/event
    {
      "router_name": "Router1",
      "source_ip": "192.168.1.1",
      "event_type": "Intrusion",
      "description": "Attempt to access the router"
    }
