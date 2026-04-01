from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid
from datetime import datetime
from enum import Enum as PyEnum

class ProjectRole(str, PyEnum):
    PO = "product_owner"
    BA = "business_analyst"
    DEVELOPER = "developer"
    STAKEHOLDER = "stakeholder"

class Domain(Base):
    __tablename__ = "domains"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    name_ar = Column(String(100), nullable=False)
    country = Column(String(10), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domains.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_text_ar = Column(Text, nullable=False)
    question_order = Column(String(10), nullable=False)
    is_active = Column(Boolean, default=True)

class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domains.id"), nullable=False)
    country = Column(String(10), nullable=False)
    role = Column(String(50), nullable=False, default="business_analyst")
    answers = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)