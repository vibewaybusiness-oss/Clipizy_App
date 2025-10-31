import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from api.db import Base
from sqlalchemy.dialects.postgresql import UUID as GUID


class Stats(Base):
    __tablename__ = "stats"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    export_id = Column(GUID(), ForeignKey("exports.id", ondelete="CASCADE"), nullable=False)

    platform = Column(String, nullable=False)  # youtube | instagram | tiktok
    account_name = Column(String, nullable=True)  # e.g. channel or handle
    video_url = Column(String, nullable=True)  # published link

    # 📊 Analytics
    views = Column(BigInteger, default=0)
    likes = Column(BigInteger, default=0)
    comments = Column(BigInteger, default=0)
    shares = Column(BigInteger, default=0)
    watch_time = Column(BigInteger, nullable=True)  # in seconds

    last_synced = Column(DateTime, default=datetime.utcnow)

    # Relationships
    export = relationship("Export", back_populates="stats")
