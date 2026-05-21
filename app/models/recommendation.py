from sqlalchemy import Column, Integer, JSON, Text, ForeignKey, DateTime, func
from app.database import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    allocation_json = Column(JSON, nullable=False)
    summary = Column(Text, nullable=True)
    risk_score = Column(Integer, nullable=True)
    financial_health_score = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())