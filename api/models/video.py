import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, JSON, Boolean
from sqlalchemy.orm import relationship

from api.db import Base
from sqlalchemy.dialects.postgresql import UUID as GUID


class Video(Base):
    __tablename__ = "videos"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)

    file_path = Column(String, nullable=False)  # e.g. video/video1.mp4
    type = Column(String, default="draft")  # draft | final | intro_animation | outro_animation
    status = Column(String, default="pending")  # pending | processing | complete
    prompts = Column(Text, nullable=True)  # JSON string with generation metadata
    
    # Animation specific fields
    is_intro_animation = Column(Boolean, default=False)
    is_outro_animation = Column(Boolean, default=False)
    animation_duration = Column(Integer, nullable=True)  # Duration in seconds
    animation_style = Column(String, nullable=True)  # smooth | dynamic | static

    # 📊 Metadata
    duration = Column(Integer, nullable=True)  # in seconds
    format = Column(String, nullable=True)  # mp4 | mov | avi
    resolution = Column(String, nullable=True)  # 720p | 1080p | 4k
    aspect_ratio = Column(String, nullable=True)  # 16:9 | 9:16 | 1:1
    size_mb = Column(Integer, nullable=True)
    video_metadata = Column(JSON, nullable=True)  # Flexible metadata storage

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="videos")
