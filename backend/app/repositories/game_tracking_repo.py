from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from typing import Optional, List
from datetime import datetime, timedelta
from ..models.game_session import GameSession, UserAchievement


class GameTrackingRepository:
    """Repository for game tracking database operations"""

    def __init__(self, db: Session):
        self.db = db

    # Game Session Methods
    def create_session(self, user_id: int, game_type: str, game_name: str,
                      pre_mood: Optional[int] = None, device: Optional[str] = None) -> GameSession:
        """Create a new game session"""
        session = GameSession(
            user_id=user_id,
            game_type=game_type,
            game_name=game_name,
            pre_mood=pre_mood,
            device=device,
            started_at=datetime.utcnow()
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def complete_session(self, session_id: int, post_mood: Optional[int] = None,
                        effectiveness_rating: Optional[int] = None, notes: Optional[str] = None) -> GameSession:
        """Complete a game session"""
        session = self.db.query(GameSession).filter(GameSession.id == session_id).first()
        if session:
            session.completed = True
            session.completed_at = datetime.utcnow()
            session.post_mood = post_mood
            session.effectiveness_rating = effectiveness_rating
            session.notes = notes

            # Calculate duration
            if session.started_at and session.completed_at:
                duration = (session.completed_at - session.started_at).total_seconds()
                session.duration_seconds = int(duration)

            # Calculate mood improvement
            if session.pre_mood and session.post_mood:
                session.mood_improvement = session.post_mood - session.pre_mood

            self.db.commit()
            self.db.refresh(session)
        return session

    def get_session_by_id(self, session_id: int) -> Optional[GameSession]:
        """Get a session by ID"""
        return self.db.query(GameSession).filter(GameSession.id == session_id).first()

    def get_user_sessions(self, user_id: int, limit: int = 50) -> List[GameSession]:
        """Get user's recent sessions"""
        return self.db.query(GameSession)\
            .filter(GameSession.user_id == user_id)\
            .order_by(GameSession.started_at.desc())\
            .limit(limit)\
            .all()

    def get_total_sessions(self, user_id: int) -> int:
        """Get total number of sessions"""
        return self.db.query(GameSession)\
            .filter(GameSession.user_id == user_id)\
            .count()

    def get_completed_sessions(self, user_id: int) -> int:
        """Get total completed sessions"""
        return self.db.query(GameSession)\
            .filter(and_(GameSession.user_id == user_id, GameSession.completed == True))\
            .count()

    def get_total_duration(self, user_id: int) -> int:
        """Get total duration in seconds"""
        result = self.db.query(func.sum(GameSession.duration_seconds))\
            .filter(and_(GameSession.user_id == user_id, GameSession.completed == True))\
            .scalar()
        return result or 0

    def get_sessions_by_game_type(self, user_id: int, game_type: str) -> List[GameSession]:
        """Get sessions for a specific game type"""
        return self.db.query(GameSession)\
            .filter(and_(GameSession.user_id == user_id, GameSession.game_type == game_type))\
            .all()

    def get_weekly_sessions(self, user_id: int) -> int:
        """Get sessions from last 7 days"""
        week_ago = datetime.utcnow() - timedelta(days=7)
        return self.db.query(GameSession)\
            .filter(and_(
                GameSession.user_id == user_id,
                GameSession.started_at >= week_ago
            ))\
            .count()

    def get_monthly_sessions(self, user_id: int) -> int:
        """Get sessions from last 30 days"""
        month_ago = datetime.utcnow() - timedelta(days=30)
        return self.db.query(GameSession)\
            .filter(and_(
                GameSession.user_id == user_id,
                GameSession.started_at >= month_ago
            ))\
            .count()

    def get_current_streak(self, user_id: int) -> int:
        """Calculate current consecutive days streak"""
        sessions = self.db.query(GameSession)\
            .filter(GameSession.user_id == user_id)\
            .order_by(GameSession.started_at.desc())\
            .all()

        if not sessions:
            return 0

        # Get unique dates
        dates = sorted(set(s.started_at.date() for s in sessions), reverse=True)

        if not dates:
            return 0

        # Check if today or yesterday was active
        today = datetime.utcnow().date()
        if dates[0] != today and dates[0] != today - timedelta(days=1):
            return 0

        # Count consecutive days
        streak = 1
        for i in range(len(dates) - 1):
            if (dates[i] - dates[i + 1]).days == 1:
                streak += 1
            else:
                break

        return streak

    def get_average_mood_improvement(self, user_id: int) -> Optional[float]:
        """Get average mood improvement"""
        result = self.db.query(func.avg(GameSession.mood_improvement))\
            .filter(and_(
                GameSession.user_id == user_id,
                GameSession.mood_improvement.isnot(None)
            ))\
            .scalar()
        return round(result, 2) if result else None

    # Achievement Methods
    def create_achievement(self, user_id: int, achievement_type: str, achievement_name: str,
                          description: Optional[str] = None, icon: Optional[str] = None,
                          category: Optional[str] = None, target: Optional[int] = None) -> UserAchievement:
        """Create a new achievement"""
        achievement = UserAchievement(
            user_id=user_id,
            achievement_type=achievement_type,
            achievement_name=achievement_name,
            achievement_description=description,
            icon=icon,
            category=category,
            target=target,
            progress=0
        )
        self.db.add(achievement)
        self.db.commit()
        self.db.refresh(achievement)
        return achievement

    def get_user_achievements(self, user_id: int) -> List[UserAchievement]:
        """Get all user achievements"""
        return self.db.query(UserAchievement)\
            .filter(UserAchievement.user_id == user_id)\
            .order_by(UserAchievement.unlocked_at.desc())\
            .all()

    def get_achievement_by_type(self, user_id: int, achievement_type: str) -> Optional[UserAchievement]:
        """Get achievement by type"""
        return self.db.query(UserAchievement)\
            .filter(and_(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_type == achievement_type
            ))\
            .first()

    def update_achievement_progress(self, achievement_id: int, progress: int) -> UserAchievement:
        """Update achievement progress"""
        achievement = self.db.query(UserAchievement)\
            .filter(UserAchievement.id == achievement_id)\
            .first()
        if achievement:
            achievement.progress = progress
            self.db.commit()
            self.db.refresh(achievement)
        return achievement
