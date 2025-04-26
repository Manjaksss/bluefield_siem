
from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import Response
from app import crud, models, database
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database setup
engine = database.engine
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.environ.get('SECRET_KEY', 'your-secret-key'))

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'password')
    if username == admin_username and password == admin_password:
        request.session['user'] = username
        return RedirectResponse("/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    events = crud.get_events()
    stats = crud.get_stats(events)
    return templates.TemplateResponse("index.html", {"request": request, "events": events, "stats": stats})

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

@app.post("/event")
async def receive_event(request: Request):
    try:
        content_type = request.headers.get('content-type', '')
        if 'application/json' in content_type:
            data = await request.json()
        elif 'application/x-www-form-urlencoded' in content_type:
            form = await request.form()
            data = {
                "router_name": form.get("Site") or form.get("router_name"),
                "source_ip": form.get("WAN") or form.get("source_ip"),
                "event_type": form.get("Description") or form.get("event_type"),
                "description": f"Time: {form.get('Time')}" if form.get('Time') else form.get("description"),
            }
        else:
            return {"error": "Unsupported Content-Type"}

        crud.insert_event(
            router_name=data.get("router_name", "Unknown Router"),
            source_ip=data.get("source_ip", "0.0.0.0"),
            event_type=data.get("event_type", "Unknown Event"),
            description=data.get("description", "No Description"),
        )
        return {"status": "Event received"}
    except Exception as e:
        return {"error": str(e)}
