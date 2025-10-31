import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from api.db import Base
from sqlalchemy.dialects.postgresql import UUID as GUID


class Audio(Base):
    __tablename__ = "audios"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)

    file_path = Column(String, nullable=False)  # e.g. audio/voiceover1.wav
    type = Column(String, nullable=True)  # voiceover | sfx | stem | other
    description = Column(String, nullable=True)

    # 📊 Metadata
    duration = Column(Integer, nullable=True)  # seconds
    format = Column(String, nullable=True)  # wav | mp3
    sample_rate = Column(Integer, nullable=True)
    channels = Column(Integer, nullable=True)
    bitrate = Column(Integer, nullable=True)
    size_mb = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="audio")
