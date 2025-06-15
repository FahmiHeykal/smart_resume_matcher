from sqlalchemy.orm import Session
from app.models.resume import Resume
from app.models.job import Job

def calculate_match_score(resume_text_or_id, job_text_or_id, db: Session = None) -> float:
    if isinstance(resume_text_or_id, str) and isinstance(job_text_or_id, str):
        resume_text = resume_text_or_id
        job_text = job_text_or_id

    elif isinstance(resume_text_or_id, int) and isinstance(job_text_or_id, int):
        if db is None:
            raise ValueError("Database session required when using IDs")
        resume = db.query(Resume).filter_by(id=resume_text_or_id).first()
        job = db.query(Job).filter_by(id=job_text_or_id).first()
        if not resume or not job:
            raise ValueError("Resume or Job not found")
        resume_text = resume.content
        job_text = job.description

    else:
        raise ValueError("Invalid input type")

    resume_words = set(resume_text.lower().split())
    job_words = set(job_text.lower().split())
    if not job_words:
        return 0.0

    match_count = len(resume_words & job_words)
    score = round(match_count / len(job_words), 3)
    return score
