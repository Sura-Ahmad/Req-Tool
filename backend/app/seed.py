from app.database import SessionLocal
from app.models.domain import Domain, Question
import uuid

def seed():
    db = SessionLocal()
    
    # Check if already seeded
    if db.query(Domain).first():
        print("Already seeded!")
        db.close()
        return

    # Jordan domains
    health = Domain(id=uuid.uuid4(), name="Health", name_ar="الصحة", country="JO")
    education = Domain(id=uuid.uuid4(), name="Education", name_ar="التعليم", country="JO")
    finance = Domain(id=uuid.uuid4(), name="Finance", name_ar="المالية", country="JO")

    db.add_all([health, education, finance])
    db.commit()

    # Health questions
    health_questions = [
        Question(domain_id=health.id, question_text="What type of health system are you building?", question_text_ar="ما نوع النظام الصحي الذي تبنيه؟", question_order="1"),
        Question(domain_id=health.id, question_text="Who are the main users of the system?", question_text_ar="من هم المستخدمون الرئيسيون للنظام؟", question_order="2"),
        Question(domain_id=health.id, question_text="Does the system need to integrate with existing hospital systems?", question_text_ar="هل يحتاج النظام للتكامل مع أنظمة المستشفيات الموجودة؟", question_order="3"),
    ]

    # Education questions
    education_questions = [
        Question(domain_id=education.id, question_text="What type of educational system are you building?", question_text_ar="ما نوع النظام التعليمي الذي تبنيه؟", question_order="1"),
        Question(domain_id=education.id, question_text="What is the target age group?", question_text_ar="ما هي الفئة العمرية المستهدفة؟", question_order="2"),
        Question(domain_id=education.id, question_text="Does the system need to support online learning?", question_text_ar="هل يحتاج النظام لدعم التعلم عن بعد؟", question_order="3"),
    ]

    db.add_all(health_questions + education_questions)
    db.commit()
    db.close()
    print("Seeded successfully!")

if __name__ == "__main__":
    seed()