from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.auth import SECRET_KEY, ALGORITHM
from app.database import Base, engine
from app.models import User, RoleEnum
from app.auth import verify_password, create_access_token
from app.dependencies import get_db

# Routers
from app.routes import admin, manager, employee
from app import auth  # auth router (logout)

# ---------------- Create tables ----------------
Base.metadata.create_all(bind=engine)

# ---------------- FastAPI app ----------------
app = FastAPI(title="Task Management System")

# ---------------- Templates & Static ----------------
# Use top-level templates/ and static/ directories so Jinja2 and StaticFiles
# can find the files that live at the project root `templates/` and `static/`.
templates = Jinja2Templates(directory="templates")
# Mount static so templates can reference /static/... URLs
app.mount("/static", StaticFiles(directory="static"), name="static")

# Make the `static` url helper available in templates
templates.env.globals['static'] = lambda path: f"/static/{path.lstrip('/')}"

# ---------------- Include Routers ----------------
app.include_router(admin.router)  # prefix is already /admin in router
app.include_router(manager.router)  # prefix is already /manager
app.include_router(employee.router)  # prefix is already /employee
app.include_router(auth.router)  # logout, etc.


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# ------------- Form login (HTML) -------------
@app.post("/login")
def login_form(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        # Return login page with error message and preserve username
        return templates.TemplateResponse("login.html", {"request": request, "error": "Incorrect username or password", "username": username}, status_code=401)

    access_token = create_access_token(data={"sub": user.username})
    # Choose redirect based on role
    if user.role == RoleEnum.admin:
        redirect_url = "/admin/dashboard"
    elif user.role == RoleEnum.manager:
        redirect_url = "/manager/dashboard"
    else:
        redirect_url = "/employee/dashboard"

    response = RedirectResponse(url=redirect_url, status_code=303)
    # set httponly cookie so browser forms can authenticate HTML pages
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=60*60)
    return response

# ---------------- Login Page ----------------
@app.get("/login", response_class=HTMLResponse)
def show_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# ---------------- Root ----------------
@app.get("/")
def read_root():
    # Redirect browser root to login page as the first route
    return RedirectResponse(url="/login")



@app.middleware("http")
async def add_current_user_to_request(request: Request, call_next):
    """Middleware to decode JWT cookie and attach user object to request.state"""
    token = request.cookies.get("access_token")
    request.state.user = None
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username:
                db = next(get_db())
                user = db.query(User).filter(User.username == username).first()
                request.state.user = user
        except JWTError:
            pass  # ignore expired/invalid token
    response = await call_next(request)
    return response

