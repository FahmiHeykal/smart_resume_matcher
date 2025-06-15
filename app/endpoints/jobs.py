from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.job import Job
from app.models.user import User, UserRole
from app.models.resume import Resume
from app.schemas.job import JobCreate, JobUpdate, JobOut
from app.endpoints.resumes import get_current_user
from app.services.matcher import calculate_match_score

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/", response_model=JobOut)
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    new_job = Job(**job.dict())
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job


@router.get("/", response_model=List[JobOut])
def list_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()


@router.get("/match", response_model=List[dict])
def match_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.candidate:
        raise HTTPException(status_code=403, detail="Only candidates can match jobs")

    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    if not resumes:
        raise HTTPException(status_code=404, detail="No resumes found")

    jobs = db.query(Job).all()
    cv_text = " ".join([resume.content for resume in resumes])

    results = [
        {
            "job": job,
            "match_score": calculate_match_score(cv_text, job.required_skills)
        }
        for job in jobs
    ]

    results.sort(key=lambda r: r["match_score"], reverse=True)

    return [
        {
            "job_id": r["job"].id,
            "title": r["job"].title,
            "match_score": r["match_score"]
        }
        for r in results
    ]


@router.put("/{job_id}", response_model=JobOut)
def update_job(
    job_id: int,
    job_update: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    for field, value in job_update.dict(exclude_unset=True).items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    db.delete(job)
    db.commit()
