from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.crud import stats

router = APIRouter(prefix="/stats", tags=["Statistics"])

@router.get("/totals")
def get_totals(db: Session = Depends(get_db)):
    return {
        "total_resumes": stats.get_total_resumes(db),
        "total_jobs": stats.get_total_jobs(db),
        "total_matches": stats.get_total_matches(db),
    }

@router.get("/matches-per-candidate")
def get_matches_per_candidate(db: Session = Depends(get_db)):
    return stats.get_match_count_per_candidate(db)

@router.get("/most-applied-jobs")
def get_most_applied_jobs(limit: int = 5, db: Session = Depends(get_db)):
    return stats.get_most_applied_jobs(db, limit=limit)
