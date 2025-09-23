from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import Base

class AssetService(Base):
    __tablename__ = "asset_services"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"))
    port = Column(Integer, nullable=False)
    protocol = Column(String, nullable=False)   # tcp|udp
    service_name = Column(String)
    banner = Column(Text)

    asset = relationship("Asset", back_populates="services")
    vulnerabilities = relationship("Vulnerability", back_populates="service", cascade="all, delete-orphan")
