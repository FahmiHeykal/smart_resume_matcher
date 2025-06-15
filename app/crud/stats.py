from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import User, Resume, Job, MatchResult

def get_total_resumes(db: Session) -> int:
    return db.query(func.count(Resume.id)).scalar()

def get_total_jobs(db: Session) -> int:
    return db.query(func.count(Job.id)).scalar()

def get_total_matches(db: Session) -> int:
    return db.query(func.count(MatchResult.id)).scalar()

def get_match_count_per_candidate(db: Session):
    return (
        db.query(User.id, User.name, func.count(MatchResult.id).label("match_count"))
        .join(Resume, Resume.user_id == User.id)
        .join(MatchResult, MatchResult.resume_id == Resume.id)
        .group_by(User.id)
        .all()
    )

def get_most_applied_jobs(db: Session, limit: int = 5):
    return (
        db.query(Job.id, Job.title, func.count(MatchResult.id).label("applications"))
        .join(MatchResult, MatchResult.job_id == Job.id)
        .group_by(Job.id)
        .order_by(func.count(MatchResult.id).desc())
        .limit(limit)
        .all()
    )