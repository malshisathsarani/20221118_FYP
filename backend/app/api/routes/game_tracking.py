from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...schemas.game_tracking import (
    GameSessionStart, GameSessionComplete, GameSessionResponse,
    ProgressSummary, GameStats, WeeklyActivity, MoodTrends,
    AchievementResponse, SessionCompleteResponse
)
from ...services.game_tracking_service import GameTrackingService
from ...models.user import User
from ..dependencies import get_current_user

router = APIRouter()


@router.post("/sessions/start", response_model=GameSessionResponse, status_code=status.HTTP_201_CREATED)
def start_game_session(
    session_data: GameSessionStart,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a new game/wellness tool session.

    Endpoint: POST /api/games/sessions/start

    Headers:
    - Authorization: Bearer <access_token>

    Request body:
    - game_type: Type of game (breathing, puzzle, drawing, coloring)
    - game_name: Display name
    - pre_mood: Optional mood rating (1-5)
    - device: Optional device type

    Returns:
    - GameSessionResponse with session details
    """
    service = GameTrackingService(db)
    session = service.start_session(current_user.id, session_data)
    return GameSessionResponse.model_validate(session)


@router.put("/sessions/{session_id}/complete", response_model=SessionCompleteResponse)
def complete_game_session(
    session_id: int,
    completion_data: GameSessionComplete,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete a game session and unlock achievements.

    Endpoint: PUT /api/games/sessions/{session_id}/complete

    Headers:
    - Authorization: Bearer <access_token>

    Request body:
    - post_mood: Optional mood rating after (1-5)
    - effectiveness_rating: How helpful (1-5 stars)
    - notes: Optional notes

    Returns:
    - SessionCompleteResponse with session details, new achievements, and progress
    """
    service = GameTrackingService(db)
    return service.complete_session(current_user.id, session_id, completion_data)


@router.get("/progress/summary", response_model=ProgressSummary)
def get_progress_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's overall progress summary.

    Endpoint: GET /api/games/progress/summary

    Headers:
    - Authorization: Bearer <access_token>

    Returns:
    - ProgressSummary with stats, streaks, and achievements
    """
    service = GameTrackingService(db)
    return service.get_progress_summary(current_user.id)


@router.get("/stats/games", response_model=List[GameStats])
def get_game_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics for each game type.

    Endpoint: GET /api/games/stats/games

    Headers:
    - Authorization: Bearer <access_token>

    Returns:
    - List of GameStats with details for each game
    """
    service = GameTrackingService(db)
    return service.get_game_stats(current_user.id)


@router.get("/stats/weekly", response_model=WeeklyActivity)
def get_weekly_activity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get activity breakdown by day of week.

    Endpoint: GET /api/games/stats/weekly

    Headers:
    - Authorization: Bearer <access_token>

    Returns:
    - WeeklyActivity with session counts per day
    """
    service = GameTrackingService(db)
    return service.get_weekly_activity(current_user.id)


@router.get("/stats/mood", response_model=MoodTrends)
def get_mood_trends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get mood improvement trends.

    Endpoint: GET /api/games/stats/mood

    Headers:
    - Authorization: Bearer <access_token>

    Returns:
    - MoodTrends with average moods and improvements
    """
    service = GameTrackingService(db)
    return service.get_mood_trends(current_user.id)


@router.get("/achievements", response_model=List[AchievementResponse])
def get_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's unlocked achievements.

    Endpoint: GET /api/games/achievements

    Headers:
    - Authorization: Bearer <access_token>

    Returns:
    - List of AchievementResponse
    """
    service = GameTrackingService(db)
    return service.get_achievements(current_user.id)


@router.get("/sessions/history", response_model=List[GameSessionResponse])
def get_session_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's recent game sessions.

    Endpoint: GET /api/games/sessions/history?limit=50

    Headers:
    - Authorization: Bearer <access_token>

    Query params:
    - limit: Number of sessions to return (default 50)

    Returns:
    - List of GameSessionResponse
    """
    from ...repositories.game_tracking_repo import GameTrackingRepository
    repo = GameTrackingRepository(db)
    sessions = repo.get_user_sessions(current_user.id, limit)
    return [GameSessionResponse.model_validate(s) for s in sessions]
