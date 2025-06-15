from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.resume import Resume
from app.models.job import Job
from app.models.resume_summary import ResumeSummary
from app.endpoints.resumes import get_current_user
from app.services.recommender import get_skill_gap, recommend_trainings_for_skills

router = APIRouter(prefix="/trainings", tags=["Trainings"])

@router.get("/recommend/{job_id}")
def recommend_training(job_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    if not resumes:
        raise HTTPException(404, "No resumes found")

    summary = None
    for r in resumes:
        if r.summary:
            summary = r.summary
            break
    if not summary:
        raise HTTPException(404, "No resume summary found")

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")

    skill_gap = get_skill_gap(summary.skills, job.required_skills)
    recommendations = recommend_trainings_for_skills(skill_gap)

    return {
        "job_title": job.title,
        "skill_gap": skill_gap,
        "recommended_trainings": recommendations
    }
