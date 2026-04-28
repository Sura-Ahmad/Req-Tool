"""Run from backend/ directory: python scripts/create_admin.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import hash_password

def main():
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == "admin@admin.com").first():
            print("Admin user already exists.")
            return
        admin = User(
            email="admin@admin.com",
            password_hash=hash_password("admin123"),
            full_name="Admin",
            role=UserRole.admin,
        )
        db.add(admin)
        db.commit()
        print("Admin created — email: admin@admin.com  password: admin123")
    finally:
        db.close()

if __name__ == "__main__":
    main()
