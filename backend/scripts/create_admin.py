"""Run from backend/ directory: python scripts/create_admin.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import hash_password

def ensure_admin(db, email: str, full_name: str):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        existing.role = UserRole.admin
        existing.is_active = True
        existing.password_hash = hash_password("admin123")
        db.commit()
        print(f"Reset: {email}  password: admin123")
    else:
        admin = User(
            email=email,
            password_hash=hash_password("admin123"),
            full_name=full_name,
            role=UserRole.admin,
        )
        db.add(admin)
        db.commit()
        print(f"Created: {email}  password: admin123")

def main():
    db = SessionLocal()
    try:
        ensure_admin(db, "admin@admin.com", "Admin")
        ensure_admin(db, "admin2@admin.com", "Admin2")
    finally:
        db.close()

if __name__ == "__main__":
    main()
