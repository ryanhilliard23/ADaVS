from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default="pending", nullable=False) # pending | running | completed | failed
    targets = Column(String(255), nullable=False)

    assets = relationship("Asset", back_populates="scan", cascade="all, delete-orphan")