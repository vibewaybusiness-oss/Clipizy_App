import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from api.db import Base
from sqlalchemy.dialects.postgresql import UUID as GUID


class Export(Base):
    __tablename__ = "exports"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)

    file_path = Column(String, nullable=False)  # final_video/final_v1.mp4
    format = Column(String, nullable=True)  # mp4 | mov | gif
    resolution = Column(String, nullable=True)  # 720p | 1080p | 4k
    aspect_ratio = Column(String, nullable=True)  # 16:9 | 9:16
    duration = Column(Integer, nullable=True)  # seconds
    size_mb = Column(Integer, nullable=True)

    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="exports")
    stats = relationship("Stats", back_populates="export", cascade="all, delete-orphan")
