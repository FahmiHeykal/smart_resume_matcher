from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from passlib.context import CryptContext

def create_default_user():
    db: Session = SessionLocal()
    user = db.query(User).filter(User.email == "fahmi@example.com").first()
    if not user:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_pw = pwd_context.hash("password123")
        new_user = User(
            name="Fahmi",
            email="fahmi@example.com",
            hashed_password=hashed_pw,
            role=UserRole.admin
        )
        db.add(new_user)
        db.commit()
        print("User default berhasil dibuat: fahmi@example.com / password123")
    db.close()
