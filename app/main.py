
from fastapi import FastAPI, Request, Form, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app import crud, database, models
import os

app = FastAPI()

# Secret key for sessions
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "supersecretkey"))

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

models.Base.metadata.create_all(bind=database.engine)

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == os.getenv("ADMIN_USERNAME", "admin") and password == os.getenv("ADMIN_PASSWORD", "password"):
        request.session["user"] = username
        return RedirectResponse("/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if "user" not in request.session:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    events = crud.get_events()
    stats = crud.get_stats()
    return templates.TemplateResponse("index.html", {"request": request, "events": events, "stats": stats})

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

@app.post("/event")
async def receive_event(router_name: str, source_ip: str, event_type: str, description: str):
    crud.create_event(router_name, source_ip, event_type, description)
    return {"message": "Event received successfully"}
