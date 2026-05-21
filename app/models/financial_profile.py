from sqlalchemy import Column, Integer, Float, String, JSON, ForeignKey, DateTime, func
from app.database import Base


class FinancialProfile(Base):
    __tablename__ = "financial_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    monthly_income = Column(Float, nullable=False)
    monthly_expenses = Column(Float, nullable=False)
    emergency_fund = Column(Float, default=0.0, nullable=False)
    savings = Column(Float, default=0.0)
    debts = Column(Float, default=0.0)
    risk_profile = Column(String, default="moderate")  # conservative / moderate / aggressive
    financial_goals = Column(JSON, default=list)  # ["house", "retirement", "emergency"]
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
