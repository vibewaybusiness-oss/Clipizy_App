import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, Text, func
from sqlalchemy.orm import relationship

from api.db import Base
from sqlalchemy.dialects.postgresql import UUID


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)  # if using local auth

    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")
    social_accounts = relationship("SocialAccount", back_populates="user", cascade="all, delete-orphan")
    credits_transactions = relationship("CreditsTransaction", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")

    # Profile
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)

    # 🔑 Global settings
    settings = Column(JSON, nullable=True)
    # Example:
    # {
    #   "default_project_type": "music-clip",
    #   "notifications": true,
    #   "preferred_format": "mp4"
    # }

    # 💰 Pricing & usage
    plan = Column(String, default="free")
    billing_id = Column(String, nullable=True)
    total_projects = Column(String(10), default="0", nullable=False)
    storage_used_bytes = Column(String(20), default="0", nullable=False)

    # 💎 Credits system
    credits_balance = Column(Integer, default=60, nullable=False)
    total_credits_earned = Column(Integer, default=60, nullable=False)
    total_credits_spent = Column(Integer, default=0, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
