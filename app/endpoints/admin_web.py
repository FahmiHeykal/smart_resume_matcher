from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db.session import get_db
from app.models.user import User
from app.models.job import Job
from app.core.security import authenticate_user, create_access_token, hash_password
from app.core.config import settings
from app.schemas.user import UserCreate

router = APIRouter(tags=["Web Login & Dashboard"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/admin/login", response_class=HTMLResponse)
def login_admin_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/admin/login")
def login_admin_process(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, email, password)
    if not user or user.role != "admin":
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "Invalid credentials"},
            status_code=401
        )
    
    token = create_access_token(
        {"sub": user.email},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    response = RedirectResponse("/admin/dashboard", status_code=302)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response

@router.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).all()
    jobs = db.query(Job).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "users": users, "jobs": jobs})

@router.get("/login", response_class=HTMLResponse)
def login_user_page(request: Request):
    return templates.TemplateResponse("user_login.html", {"request": request})

@router.post("/login")
def login_user_process(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse(
            "user_login.html", {"request": request, "error": "Invalid credentials"},
            status_code=401
        )

    token = create_access_token(
        {"sub": user.email},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    response = RedirectResponse("/dashboard", status_code=302)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response

@router.get("/dashboard", response_class=HTMLResponse)
def user_dashboard(request: Request, db: Session = Depends(get_db)):
    jobs = db.query(Job).all()
    return templates.TemplateResponse("user_dashboard.html", {"request": request, "jobs": jobs})

@router.post("/register")
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(user_in.password)
    
    new_user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hashed_password,
        role="candidate"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User registered successfully", "user_id": new_user.id}
