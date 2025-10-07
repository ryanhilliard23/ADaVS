from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id", ondelete="CASCADE"))
    ip_address = Column(String(45), nullable=False)  # enough for IPv4/IPv6
    hostname = Column(String(255))
    os = Column(String(100))

    scan = relationship("Scan", back_populates="assets")
    services = relationship("AssetService", back_populates="asset", cascade="all, delete-orphan")

