import sys, os, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import hash_password


def ensure_admin(db, email: str, full_name: str, password: str):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        existing.role = UserRole.admin
        existing.is_active = True
        existing.password_hash = hash_password(password)
        db.commit()
        print(f"Reset: {email}")
    else:
        db.add(User(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            role=UserRole.admin,
        ))
        db.commit()
        print(f"Created: {email}")


def main():
    parser = argparse.ArgumentParser(description="Create or reset an admin user")
    parser.add_argument("--email", required=True, help="Admin email address")
    parser.add_argument("--name", required=True, help="Admin full name")
    parser.add_argument("--password", required=True, help="Admin password")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        ensure_admin(db, args.email, args.name, args.password)
    finally:
        db.close()


if __name__ == "__main__":
    main()
