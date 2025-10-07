from sqlalchemy import Column, Integer, String, SmallInteger, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import Base

class AssetService(Base):
    __tablename__ = "asset_services"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"))
    port = Column(SmallInteger, nullable=False)  # ports 0-65535 fit in SmallInteger
    protocol = Column(String(10), nullable=False)   # tcp/udp
    service_name = Column(String(100))
    banner = Column(Text)

    asset = relationship("Asset", back_populates="services")
    vulnerabilities = relationship("Vulnerability", back_populates="service", cascade="all, delete-orphan")

