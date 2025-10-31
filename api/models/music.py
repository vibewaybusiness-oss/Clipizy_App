import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from api.db import Base
from sqlalchemy.dialects.postgresql import UUID as GUID


class Track(Base):
    __tablename__ = "tracks"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)

    title = Column(String, nullable=True)  # Optional title
    file_path = Column(String, nullable=False)  # e.g. music/track1.wav
    ai_generated = Column(Boolean, default=False)
    prompt = Column(String, nullable=True)  # AI generation prompt
    genre = Column(String, nullable=True)  # Music genre
    instrumental = Column(Boolean, default=False)  # Is instrumental
    video_description = Column(String, nullable=True)  # Video description
    description = Column(String, nullable=True)  # General description
    vibe = Column(String, nullable=True)  # mood / genre tag
    lyrics = Column(String, nullable=True)  # optional lyrics text
    version = Column(Integer, default=1)
    status = Column(String, default="uploaded")  # uploaded, processing, completed, error

    # 📊 Metadata (stored as JSON for flexibility)
    track_metadata = Column(JSON, nullable=True)  # Flexible metadata storage
    analysis = Column(JSON, nullable=True)  # Analysis results

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="tracks")
