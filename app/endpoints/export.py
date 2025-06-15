from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.endpoints.resumes import get_current_user
from app.models.resume import Resume
from app.models.resume_summary import ResumeSummary
from app.models.job import Job
from app.services.matcher import calculate_match_score
from app.services.recommender import get_skill_gap, recommend_trainings_for_skills
from app.utils.pdf_exporter import generate_match_report

router = APIRouter(prefix="/export", tags=["Export"])

@router.get("/pdf/{job_id}")
def export_pdf(job_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
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

    cv_text = " ".join([r.content for r in resumes])
    score = calculate_match_score(cv_text, job.required_skills)

    skill_gap = get_skill_gap(summary.skills, job.required_skills)
    trainings = recommend_trainings_for_skills(skill_gap)

    pdf_bytes = generate_match_report(job.title, score, skill_gap, trainings)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=job_match_{job_id}.pdf"}
    )
