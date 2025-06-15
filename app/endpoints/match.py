from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, constr, PositiveInt
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.core.matching import calculate_match_score
from app.models.match_result import MatchResult
from app.models.resume import Resume
from app.models.job import Job
from app.schemas.match import MatchResultCreate, MatchResultOut, MatchResultWithJobOut

router = APIRouter(prefix="/match", tags=["Match"])

class MatchRequest(BaseModel):
    resume_text: constr(strip_whitespace=True, min_length=1)
    job_description: constr(strip_whitespace=True, min_length=1)

class MatchResponse(BaseModel):
    score: float

@router.post("/text", response_model=MatchResponse)
def match_by_text(data: MatchRequest):
    try:
        score = calculate_match_score(data.resume_text, data.job_description)
        return {"score": score}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saat menghitung skor: {str(e)}"
        )

@router.post("/resume", response_model=MatchResultOut)
def match_by_id(data: MatchResultCreate, db: Session = Depends(get_db)):
    # Validasi resume_id dan job_id positif
    if data.resume_id <= 0 or data.job_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="resume_id dan job_id harus bernilai positif dan bukan nol"
        )
    
    try:
        existing = db.query(MatchResult).filter_by(
            resume_id=data.resume_id,
            job_id=data.job_id
        ).first()
        if existing:
            return existing

        resume = db.query(Resume).filter_by(id=data.resume_id).first()
        job = db.query(Job).filter_by(id=data.job_id).first()

        if not resume or not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume atau Job tidak ditemukan"
            )

        score = calculate_match_score(resume.content, job.description)

        match_result = MatchResult(
            resume_id=data.resume_id,
            job_id=data.job_id,
            score=score
        )
        db.add(match_result)
        db.commit()
        db.refresh(match_result)

        return match_result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saat proses matching: {str(e)}"
        )

@router.get("/result/{resume_id}/{job_id}", response_model=MatchResultOut)
def get_match_result(resume_id: int, job_id: int, db: Session = Depends(get_db)):
    if resume_id <= 0 or job_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="resume_id dan job_id harus bernilai positif dan bukan nol"
        )
    try:
        result = db.query(MatchResult).filter_by(resume_id=resume_id, job_id=job_id).first()
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match result not found")
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saat mengambil hasil match: {str(e)}"
        )
@router.get("/ranked/{resume_id}", response_model=List[MatchResultOut])
def get_ranked_matches(resume_id: int, db: Session = Depends(get_db)):
    if resume_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="resume_id harus bernilai positif dan bukan nol"
        )
    try:
        results = (
            db.query(MatchResult)
            .filter(MatchResult.resume_id == resume_id)
            .order_by(MatchResult.score.desc())
            .all()
        )
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tidak ditemukan hasil pencocokan untuk resume ini"
            )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saat mengambil hasil ranked match: {str(e)}"
        )

@router.get("/by-user/{user_id}", response_model=List[MatchResultOut])
def get_matches_by_user(user_id: int, db: Session = Depends(get_db)):
    if user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="user_id harus bernilai positif dan bukan nol"
        )
    try:
        results = (
            db.query(MatchResult)
            .join(Resume, Resume.id == MatchResult.resume_id)
            .filter(Resume.user_id == user_id)
            .order_by(MatchResult.score.desc())
            .all()
        )
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tidak ditemukan hasil pencocokan untuk user ini"
            )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saat mengambil hasil match berdasarkan user: {str(e)}"
        )

@router.get("/recommend/{resume_id}", response_model=List[MatchResultOut])
def recommend_jobs(resume_id: int, top_n: int = 5, db: Session = Depends(get_db)):
    if resume_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="resume_id harus bernilai positif dan bukan nol"
        )
    if top_n <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="top_n harus bernilai positif dan bukan nol"
        )
    try:
        resume = db.query(Resume).filter_by(id=resume_id).first()
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume tidak ditemukan"
            )

        jobs = db.query(Job).all()
        results = []
        for job in jobs:
            score = calculate_match_score(resume.content, job.description)
            results.append(MatchResultOut(
                resume_id=resume.id,
                job_id=job.id,
                score=score
            ))

        sorted_results = sorted(results, key=lambda x: x.score, reverse=True)
        return sorted_results[:top_n]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saat merekomendasikan pekerjaan: {str(e)}"
        )

@router.get("/history/{resume_id}", response_model=List[MatchResultOut])
def get_match_history(resume_id: int, db: Session = Depends(get_db)):
    if resume_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="resume_id harus bernilai positif dan bukan nol"
        )
    try:
        results = (
            db.query(MatchResult)
            .filter(MatchResult.resume_id == resume_id)
            .order_by(MatchResult.score.desc())
            .all()
        )
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tidak ditemukan riwayat pencocokan untuk resume ini"
            )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saat mengambil riwayat pencocokan: {str(e)}"
        )

@router.get("/recommend/{resume_id}", response_model=List[MatchResultOut])
def recommend_jobs(
    resume_id: int,
    top_n: int = 5,
    category: str = None,
    location: str = None,
    keyword: str = None,
    db: Session = Depends(get_db)
):
    if resume_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="resume_id harus bernilai positif dan bukan nol"
        )
    if top_n <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="top_n harus bernilai positif dan bukan nol"
        )
    
    try:
        resume = db.query(Resume).filter_by(id=resume_id).first()
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume tidak ditemukan"
            )

        query = db.query(Job)
        if category:
            query = query.filter(Job.category.ilike(f"%{category}%"))
        if location:
            query = query.filter(Job.location.ilike(f"%{location}%"))
        if keyword:
            query = query.filter(Job.description.ilike(f"%{keyword}%"))
        
        jobs = query.all()

        results = []
        for job in jobs:
            score = calculate_match_score(resume.content, job.description)
            results.append(MatchResultOut(
                resume_id=resume.id,
                job_id=job.id,
                score=score
            ))

        sorted_results = sorted(results, key=lambda x: x.score, reverse=True)
        return sorted_results[:top_n]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saat merekomendasikan pekerjaan: {str(e)}"
        )
    
@router.get("/ranked/{resume_id}", response_model=List[MatchResultOut])
def get_ranked_matches(
    resume_id: int,
    page: int = 1,
    limit: int = 10,
    keyword: str = None,
    db: Session = Depends(get_db)
):
    if resume_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="resume_id harus bernilai positif dan bukan nol"
        )
    if page <= 0 or limit <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="page dan limit harus bernilai positif dan bukan nol"
        )

    try:
        query = db.query(MatchResult).join(Job, Job.id == MatchResult.job_id).filter(
            MatchResult.resume_id == resume_id
        )

        if keyword:
            query = query.filter(Job.description.ilike(f"%{keyword}%"))

        total_results = query.count()
        results = (
            query.order_by(MatchResult.score.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tidak ditemukan hasil pencocokan"
            )

        return results

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saat mengambil hasil ranked match: {str(e)}"
        )
    
@router.get("/recommend/{resume_id}", response_model=List[MatchResultOut])
def recommend_jobs(
    resume_id: int,
    top_n: int = 5,
    category: str = None,
    location: str = None,
    db: Session = Depends(get_db)
):
    if resume_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="resume_id harus bernilai positif dan bukan nol"
        )
    if top_n <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="top_n harus bernilai positif dan bukan nol"
        )

    try:
        resume = db.query(Resume).filter_by(id=resume_id).first()
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume tidak ditemukan"
            )

        job_query = db.query(Job)

        if category:
            job_query = job_query.filter(Job.category.ilike(f"%{category}%"))
        if location:
            job_query = job_query.filter(Job.location.ilike(f"%{location}%"))

        jobs = job_query.all()

        results = []
        for job in jobs:
            score = calculate_match_score(resume.content, job.description)
            results.append(MatchResultOut(
                resume_id=resume.id,
                job_id=job.id,
                score=score
            ))

        sorted_results = sorted(results, key=lambda x: x.score, reverse=True)
        return sorted_results[:top_n]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saat merekomendasikan pekerjaan: {str(e)}"
        )

@router.get("/history/detail/{resume_id}", response_model=List[MatchResultWithJobOut])
def get_match_history_with_job_detail(resume_id: int, db: Session = Depends(get_db)):
    if resume_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="resume_id harus bernilai positif dan bukan nol"
        )

    try:
        results = (
            db.query(MatchResult, Job)
            .join(Job, MatchResult.job_id == Job.id)
            .filter(MatchResult.resume_id == resume_id)
            .order_by(MatchResult.score.desc())
            .all()
        )

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tidak ditemukan riwayat pencocokan untuk resume ini"
            )

        return [
            MatchResultWithJobOut(
                resume_id=match.resume_id,
                job_id=match.job_id,
                score=match.score,
                job_title=job.title,
                job_description=job.description,
                location=job.location,
                category=job.category
            )
            for match, job in results
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan saat mengambil riwayat detail: {str(e)}"
        )
    
@router.get("/recommend/{resume_id}", response_model=List[MatchResultOut])
def recommend_jobs(
    resume_id: int,
    top_n: int = 5,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    ...
    if category:
        jobs = db.query(Job).filter(Job.category == category).all()
    else:
        jobs = db.query(Job).all()

@router.get("/statistics")
def get_matching_statistics(db: Session = Depends(get_db)):
    try:
        total_matching = db.query(MatchResult).count()
        total_resume = db.query(Resume).count()
        total_job = db.query(Job).count()

        return {
            "total_matching": total_matching,
            "total_resume": total_resume,
            "total_job": total_job
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saat mengambil statistik: {str(e)}"
        )
    
@router.get("/resume/{resume_id}/matched-jobs")
def get_matched_jobs_for_resume(resume_id: int, db: Session = Depends(get_db)):
    if resume_id <= 0:
        raise HTTPException(
            status_code=422,
            detail="resume_id harus bernilai positif"
        )
    try:
        results = (
            db.query(MatchResult)
            .join(Job, Job.id == MatchResult.job_id)
            .filter(MatchResult.resume_id == resume_id)
            .order_by(MatchResult.score.desc())
            .all()
        )
        if not results:
            raise HTTPException(
                status_code=404,
                detail="Tidak ditemukan hasil matching untuk resume ini"
            )
        
        return [
            {
                "job_id": r.job_id,
                "job_title": r.job.title,
                "score": r.score
            }
            for r in results
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saat mengambil data matched jobs: {str(e)}"
        )
