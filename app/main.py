from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from app import crud, database, models
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import csv
import io

from dotenv import load_dotenv
import os

load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
SECRET_KEY = os.getenv("SECRET_KEY")

app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    same_site="lax",
    https_only=False
)

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.on_event("startup")
async def startup():
    database.Base.metadata.create_all(bind=database.engine)

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        request.session["user"] = username
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not request.session.get("user"):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    events = crud.get_events()
    stats = crud.get_stats(events)
    
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request,
            "events": events,
            "total_events": stats["total_events"],
            "router_counter": stats["router_counter"],
            "event_type_counter": stats["event_type_counter"],
        }
    )


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

@app.post("/event")
async def receive_event(request: Request):
    try:
        payload = await request.json()
        
        router_name = payload.get("router_name", "Unknown") or "Unknown"
        source_ip = payload.get("source_ip", "Unknown") or "Unknown"
        event_type = payload.get("event_type", "Unknown") or "Unknown"
        description = payload.get("description", "No description provided") or "No description provided"

        crud.insert_event(router_name, source_ip, event_type, description)
        return {"message": "Event received successfully"}
    
    except Exception as e:
        print(f"DEBUG - Error receiving event: {e}")
        return JSONResponse(status_code=400, content={"error": "Invalid event format"})

@app.get("/download_csv")
async def download_csv(request: Request):
    if not request.session.get("user"):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    events = crud.get_events()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Router Name", "Source IP", "Event Type", "Description", "Timestamp"])

    for event in events:
        writer.writerow([
            event.router_name,
            event.source_ip,
            event.event_type,
            event.description,
            event.timestamp
        ])

    output.seek(0)
    filename = f"events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
