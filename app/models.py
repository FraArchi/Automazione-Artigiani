from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Config(Base):
    __tablename__ = "config"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(String, nullable=False)


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, default="webhook", nullable=False)
    client_name = Column(String, nullable=True)
    client_email = Column(String, nullable=True)
    client_phone = Column(String, nullable=True)
    job_type = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    raw_payload = Column(Text, nullable=False)
    normalized_payload = Column(Text, nullable=False)
    status = Column(String, default="new", nullable=False)
    missing_fields = Column(Text, default="[]", nullable=False)
    review_summary = Column(Text, nullable=True)
    suggested_action = Column(String, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    quotes = relationship("Quote", back_populates="lead", cascade="all, delete-orphan")


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False, index=True)
    file_path = Column(String, nullable=False)
    subtotal = Column(Float, nullable=False)
    vat = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    status = Column(String, default="draft", nullable=False)
    generated_at = Column(DateTime, default=utc_now, nullable=False)
    sent_at = Column(DateTime, nullable=True)

    lead = relationship("Lead", back_populates="quotes")


class ActivityLog(Base):
    __tablename__ = "activity_log"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True, index=True)
    event_type = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    actor = Column(String, default="system", nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
