from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    allocation: dict[str, Any] = Field(default_factory=dict)
    summary: str | None = None
    risk_score: int | None = None
    financial_health_score: int | None = None
    created_at: datetime | None = None

    @classmethod
    def from_model(cls, recommendation: Any) -> "RecommendationResponse":
        return cls(
            id=recommendation.id,
            user_id=recommendation.user_id,
            allocation=recommendation.allocation_json,
            summary=recommendation.summary,
            risk_score=recommendation.risk_score,
            financial_health_score=recommendation.financial_health_score,
            created_at=recommendation.created_at,
        )
