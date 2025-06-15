from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.resume import Resume
from app.models.resume_summary import ResumeSummary
from app.schemas.resume_summary import ResumeSummaryOut
from app.services.resume_summary_generator import summarize_cv_text
from app.models.user import User
from app.endpoints.resumes import get_current_user  # Hanya ini saja

router = APIRouter(prefix="/resume-summary", tags=["Resume Summary"])

@router.post("/{resume_id}", response_model=ResumeSummaryOut)
def generate_resume_summary(
    resume_id: int = Path(..., description="ID resume"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    summary, skills = summarize_cv_text(resume.content)

    new_summary = ResumeSummary(
        resume_id=resume.id,
        summary=summary
    )
    db.add(new_summary)
    db.commit()
    db.refresh(new_summary)

    return ResumeSummaryOut(
        id=new_summary.id,
        resume_id=resume.id,
        summary=summary,
        skills=skills
    )
