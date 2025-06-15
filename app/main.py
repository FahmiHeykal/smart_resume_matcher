import os
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.db.base import Base
from app.db.session import engine
from app.models import create_default_user

from app.endpoints import (
    auth,
    resumes,
    jobs,
    resume_summary,
    training,
    export,
    admin_web,
    match,
    stats,
)

load_dotenv()

app = FastAPI(title="Smart Resume Matcher API")

Base.metadata.create_all(bind=engine)

create_default_user()

app.include_router(auth.router)
app.include_router(resumes.router)
app.include_router(jobs.router)
app.include_router(resume_summary.router)
app.include_router(training.router)
app.include_router(export.router)
app.include_router(admin_web.router)
app.include_router(match.router)
app.include_router(stats.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
