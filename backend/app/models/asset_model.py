from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True)
    ip_address = Column(String, nullable=False)
    hostname = Column(String)
    os = Column(String)
    last_seen = Column(DateTime)
    ports = relationship("Port", back_populates="asset", cascade="all, delete-orphan")
    vulnerabilities = relationship("Vulnerability", back_populates="asset", cascade="all, delete-orphan")

class Port(Base):
    __tablename__ = "ports"
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    port_number = Column(Integer)
    protocol = Column(String)
    service_name = Column(String)
    version = Column(String)
    asset = relationship("Asset", back_populates="ports")

class Vulnerability(Base):
    __tablename__ = "vulnerabilities"
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    name = Column(String)
    severity = Column(String)
    description = Column(Text)
    detected_at = Column(DateTime)
    cve_id = Column(String)
    affected_port = Column(Integer)
    asset = relationship("Asset", back_populates="vulnerabilities")