"""Run from backend/ directory: python scripts/seed.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import SessionLocal
from app.models.domain import Domain, Question
import uuid


def seed():
    db = SessionLocal()

    if db.query(Domain).first():
        print("Already seeded!")
        db.close()
        return

    health = Domain(id=uuid.uuid4(), name="Health", name_ar="", country="JO")
    education = Domain(id=uuid.uuid4(), name="Education", name_ar="", country="JO")
    finance = Domain(id=uuid.uuid4(), name="Finance", name_ar="", country="JO")

    db.add_all([health, education, finance])
    db.commit()

    db.add_all([
        Question(domain_id=health.id, question_text="What type of health system are you building?"),
        Question(domain_id=health.id, question_text="Who are the main users of the system?"),
        Question(domain_id=health.id, question_text="Does the system need to integrate with existing hospital systems?"),
        Question(domain_id=education.id, question_text="What type of educational system are you building?"),
        Question(domain_id=education.id, question_text="What is the target age group?"),
        Question(domain_id=education.id, question_text="Does the system need to support online learning?"),
        Question(domain_id=finance.id, question_text="What type of financial system are you building?"),
        Question(domain_id=finance.id, question_text="Who are the main users of the system?"),
        Question(domain_id=finance.id, question_text="Does the system need to integrate with existing banking systems?"),
    ])
    db.commit()
    db.close()
    print("Seeded successfully!")


if __name__ == "__main__":
    seed()
