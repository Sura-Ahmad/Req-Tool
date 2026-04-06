import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.domain import Domain, Question
from app.core.config import settings
import uuid

engine = create_engine(settings.TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    if not db.query(Domain).first():
        health = Domain(id=uuid.uuid4(), name="Health", name_ar="الصحة", country="JO")
        db.add(health)
        db.commit()
        q = Question(
            domain_id=health.id,
            question_text="What type of health system?",
            question_text_ar="ما نوع النظام الصحي؟",
            question_order="1"
        )
        db.add(q)
        db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)