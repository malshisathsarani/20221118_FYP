from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# Game Session Schemas
class GameSessionStart(BaseModel):
    """Schema for starting a game session"""
    game_type: str = Field(..., description="Type of game: breathing, puzzle, drawing, coloring")
    game_name: str = Field(..., description="Display name of the game")
    pre_mood: Optional[int] = Field(None, ge=1, le=5, description="Mood before game (1-5)")
    device: Optional[str] = Field(None, description="Device type: mobile or web")


class GameSessionComplete(BaseModel):
    """Schema for completing a game session"""
    post_mood: Optional[int] = Field(None, ge=1, le=5, description="Mood after game (1-5)")
    effectiveness_rating: Optional[int] = Field(None, ge=1, le=5, description="How effective was this (1-5 stars)")
    notes: Optional[str] = Field(None, max_length=500)


class GameSessionResponse(BaseModel):
    """Schema for game session response"""
    id: int
    user_id: int
    game_type: str
    game_name: str
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    completed: bool
    pre_mood: Optional[int]
    post_mood: Optional[int]
    mood_improvement: Optional[float]
    effectiveness_rating: Optional[int]
    notes: Optional[str]
    device: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Progress & Statistics Schemas
class ProgressSummary(BaseModel):
    """Summary of user's progress"""
    total_sessions: int
    total_duration_minutes: int
    current_streak_days: int
    longest_streak_days: int
    weekly_sessions: int
    monthly_sessions: int
    favorite_game: Optional[str]
    total_games_completed: int
    average_mood_improvement: Optional[float]
    achievements_unlocked: int


class GameStats(BaseModel):
    """Statistics for a specific game type"""
    game_type: str
    game_name: str
    total_sessions: int
    total_duration_minutes: int
    completion_rate: float
    average_mood_improvement: Optional[float]
    average_effectiveness: Optional[float]
    last_played: Optional[datetime]


class WeeklyActivity(BaseModel):
    """Weekly activity breakdown"""
    monday: int = 0
    tuesday: int = 0
    wednesday: int = 0
    thursday: int = 0
    friday: int = 0
    saturday: int = 0
    sunday: int = 0
    total: int = 0


class MoodTrends(BaseModel):
    """Mood improvement trends"""
    average_pre_mood: Optional[float]
    average_post_mood: Optional[float]
    average_improvement: Optional[float]
    total_sessions_with_mood: int


# Achievement Schemas
class AchievementResponse(BaseModel):
    """Schema for achievement response"""
    id: int
    achievement_type: str
    achievement_name: str
    achievement_description: Optional[str]
    unlocked_at: datetime
    progress: int
    target: Optional[int]
    icon: Optional[str]
    category: Optional[str]

    class Config:
        from_attributes = True


class NewAchievementNotification(BaseModel):
    """Notification for newly unlocked achievement"""
    achievement_type: str
    achievement_name: str
    achievement_description: Optional[str]
    icon: Optional[str]


class SessionCompleteResponse(BaseModel):
    """Response when completing a session with potential achievements"""
    session: GameSessionResponse
    new_achievements: list[NewAchievementNotification] = []
    current_streak: int
    total_sessions: int
    progress_message: str
