from fastapi import (
    APIRouter, Depends, HTTPException, Security, status,
    UploadFile, File, Query
)
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from pydantic import BaseModel
import os, uuid, shutil

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.resume import Resume
from app.schemas.resume import ResumeOut
from app.services.parser import parse_pdf_to_text
from app.services.resume_summary_generator import summarize_cv_text
from app.core.security import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/resumes", tags=["Resumes"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class ResumeUpdate(BaseModel):
    summary: str
    skills: str

def get_current_user(
    token: str = Security(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.post("/upload", response_model=ResumeOut)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    content = parse_pdf_to_text(file_path)

    try:
        summary, skills = summarize_cv_text(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error summarizing CV: {e}")

    resume = Resume(
        user_id=current_user.id,
        filename=filename,
        content=content,
        summary=summary,
        skills=skills
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return resume

@router.get("/me", response_model=list[ResumeOut])
def get_my_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    return resumes

@router.get("/search", response_model=list[ResumeOut])
def search_resumes_by_skill(
    skill: str = Query(..., min_length=1, description="Skill keyword to search resumes"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Resume).filter(Resume.skills.ilike(f"%{skill}%"))
    if current_user.role != UserRole.admin:
        query = query.filter(Resume.user_id == current_user.id)
    return query.all()

@router.get("/", response_model=list[ResumeOut])
def list_all_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin access only")
    return db.query(Resume).all()

@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume_by_id(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Resume).filter(Resume.id == resume_id)
    if current_user.role != UserRole.admin:
        query = query.filter(Resume.user_id == current_user.id)

    resume = query.first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume

@router.put("/{resume_id}", response_model=ResumeOut)
def update_resume(
    resume_id: int,
    update_data: ResumeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Resume).filter(Resume.id == resume_id)
    if current_user.role != UserRole.admin:
        query = query.filter(Resume.user_id == current_user.id)

    resume = query.first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume.summary = update_data.summary
    resume.skills = update_data.skills
    db.commit()
    db.refresh(resume)

    return resume

@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Resume).filter(Resume.id == resume_id)
    if current_user.role != UserRole.admin:
        query = query.filter(Resume.user_id == current_user.id)

    resume = query.first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    file_path = os.path.join("uploads", resume.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.delete(resume)
    db.commit()
