from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class CrisisIndicators(BaseModel):
    """Detected crisis indicators"""
    keywords: Optional[List[str]] = []
    patterns: Optional[List[str]] = []
    emotional_state: Optional[str] = None


class CrisisAlertResponse(BaseModel):
    """Crisis alert response"""
    id: int
    user_id: int
    chat_id: Optional[int] = None
    severity: str  # mild, moderate, severe, critical
    crisis_score: float = Field(..., ge=0.0, le=1.0)
    detected_indicators: Optional[str] = None  # JSON string
    intervention_provided: Optional[str] = None
    resources_shared: Optional[str] = None
    follow_up_required: bool = True
    resolved: bool = False
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CrisisDetectionRequest(BaseModel):
    """Request for crisis detection analysis"""
    message: str
    session_id: str
    emotion_data: Optional[dict] = None


class CrisisDetectionResponse(BaseModel):
    """Real-time crisis detection result"""
    is_crisis: bool
    severity: Optional[str] = None  # mild, moderate, severe, critical
    crisis_score: float = Field(..., ge=0.0, le=1.0)
    indicators: Optional[List[str]] = None
    recommended_action: Optional[str] = None
    emergency_resources: Optional[List[str]] = None


class CrisisHistoryResponse(BaseModel):
    """Crisis event history for a user"""
    user_id: int
    total_events: int
    unresolved_count: int
    events: List[CrisisAlertResponse]
    severity_breakdown: Optional[dict] = None  # {mild: 2, moderate: 1, ...}
