from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
import os

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app import models
from app.dependencies import get_db, get_current_user

# ---------------- Password & JWT Setup ----------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token", auto_error=False)

router = APIRouter(tags=["Auth"])

# ---------------- Password utils ----------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

# ---------------- JWT Token utils ----------------
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ---------------- Current User dependency ----------------
# Reuse the get_current_user from app.dependencies which supports cookie fallback
def get_current_user_dep(current_user: models.User = Depends(get_current_user)) -> models.User:
    return current_user

# ---------------- Role-based dependencies ----------------
def admin_required(current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def manager_required(current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.RoleEnum.manager:
        raise HTTPException(status_code=403, detail="Manager access required")
    return current_user

def employee_required(current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.RoleEnum.employee:
        raise HTTPException(status_code=403, detail="Employee access required")
    return current_user

# ---------------- Logout ----------------
@router.post("/logout", summary="Logout user")
def logout_user(request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # read token from Authorization header or cookie
    token = None
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1]
    if not token:
        token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No token provided")

    # Save token to revoked tokens table
    revoked_token = models.RevokedToken(token=token)
    db.add(revoked_token)
    db.commit()
    # Clear cookie and redirect to login
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token", path="/")
    return response
