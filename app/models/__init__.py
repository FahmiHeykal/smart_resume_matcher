from app.models.user import User, UserRole
from app.models.resume import Resume
from app.models.job import Job
from app.models.match_result import MatchResult
from app.models.resume_match import ResumeMatch
from app.models.resume_summary import ResumeSummary
from app.models.matching_log import MatchingLog
from app.db.session import SessionLocal
from app.core.security import hash_password

def create_default_user():
    db = SessionLocal()
    existing_admin = db.query(User).filter(User.email == "admin@example.com").first()
    if not existing_admin:
        admin = User(
            name="Admin",
            email="admin@example.com",
            hashed_password=hash_password("admin123"),
            role=UserRole.admin.value
        )
        db.add(admin)
        db.commit()
    db.close()
