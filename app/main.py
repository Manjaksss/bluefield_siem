
from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from app import crud, database, models
from fastapi.staticfiles import StaticFiles
from datetime import datetime

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="x9v82n4fpbq7s2rj1k4d6lzn8m0a3v5t7q2b9r1y6u4c0x3m8p5z7l1d6b2q0w9s")

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
    if username == "admin" and password == "admin":
        request.session["user"] = username
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not request.session.get("user"):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    events = crud.get_events()
    stats = crud.get_stats(events)
    return templates.TemplateResponse("index.html", {"request": request, "events": events, "stats": stats})

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

@app.post("/event")
async def receive_event(request: Request):
    try:
        payload = await request.json()
        router_name = payload.get("router_name", "Unknown")
        source_ip = payload.get("source_ip", "Unknown")
        event_type = payload.get("event_type", "Intrusion Attempt")
        description = payload.get("description", "No description provided")
        crud.insert_event(router_name, source_ip, event_type, description)
        return {"message": "Event received successfully"}
    except Exception as e:
        return {"error": str(e)}
