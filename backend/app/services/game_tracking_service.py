from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from collections import Counter
from ..repositories.game_tracking_repo import GameTrackingRepository
from ..schemas.game_tracking import (
    GameSessionStart, GameSessionComplete, GameSessionResponse,
    ProgressSummary, GameStats, WeeklyActivity, MoodTrends,
    AchievementResponse, SessionCompleteResponse, NewAchievementNotification
)
from ..models.game_session import GameSession


class GameTrackingService:
    """Service layer for game tracking business logic"""

    def __init__(self, db: Session):
        self.db = db
        self.repo = GameTrackingRepository(db)

    def start_session(self, user_id: int, session_data: GameSessionStart) -> GameSession:
        """Start a new game session"""
        return self.repo.create_session(
            user_id=user_id,
            game_type=session_data.game_type,
            game_name=session_data.game_name,
            pre_mood=session_data.pre_mood,
            device=session_data.device
        )

    def complete_session(self, user_id: int, session_id: int,
                        completion_data: GameSessionComplete) -> SessionCompleteResponse:
        """Complete a game session and check for achievements"""
        # Get and validate session
        session = self.repo.get_session_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to complete this session"
            )

        # Complete the session
        completed_session = self.repo.complete_session(
            session_id=session_id,
            post_mood=completion_data.post_mood,
            effectiveness_rating=completion_data.effectiveness_rating,
            notes=completion_data.notes
        )

        # Check for new achievements
        new_achievements = self._check_and_unlock_achievements(user_id, completed_session)

        # Get updated stats
        total_sessions = self.repo.get_completed_sessions(user_id)
        current_streak = self.repo.get_current_streak(user_id)

        # Create progress message
        progress_message = f"Great job! You've completed {total_sessions} sessions."
        if current_streak > 0:
            progress_message += f" Your streak: {current_streak} days! 🔥"

        return SessionCompleteResponse(
            session=GameSessionResponse.model_validate(completed_session),
            new_achievements=new_achievements,
            current_streak=current_streak,
            total_sessions=total_sessions,
            progress_message=progress_message
        )

    def get_progress_summary(self, user_id: int) -> ProgressSummary:
        """Get user's overall progress summary"""
        total_sessions = self.repo.get_total_sessions(user_id)
        completed_sessions = self.repo.get_completed_sessions(user_id)
        total_duration_seconds = self.repo.get_total_duration(user_id)
        weekly_sessions = self.repo.get_weekly_sessions(user_id)
        monthly_sessions = self.repo.get_monthly_sessions(user_id)
        current_streak = self.repo.get_current_streak(user_id)
        avg_mood_improvement = self.repo.get_average_mood_improvement(user_id)

        # Get favorite game
        sessions = self.repo.get_user_sessions(user_id, limit=1000)
        game_counts = Counter(s.game_type for s in sessions if s.completed)
        favorite_game = game_counts.most_common(1)[0][0] if game_counts else None

        # Count achievements
        achievements = self.repo.get_user_achievements(user_id)
        achievements_unlocked = len(achievements)

        # Calculate longest streak (simplified - could be enhanced)
        longest_streak = current_streak  # For now, use current as longest

        return ProgressSummary(
            total_sessions=total_sessions,
            total_duration_minutes=total_duration_seconds // 60,
            current_streak_days=current_streak,
            longest_streak_days=longest_streak,
            weekly_sessions=weekly_sessions,
            monthly_sessions=monthly_sessions,
            favorite_game=favorite_game,
            total_games_completed=completed_sessions,
            average_mood_improvement=avg_mood_improvement,
            achievements_unlocked=achievements_unlocked
        )

    def get_game_stats(self, user_id: int) -> List[GameStats]:
        """Get statistics for each game type"""
        sessions = self.repo.get_user_sessions(user_id, limit=1000)

        # Group by game type
        game_data = {}
        for session in sessions:
            if session.game_type not in game_data:
                game_data[session.game_type] = {
                    'sessions': [],
                    'game_name': session.game_name
                }
            game_data[session.game_type]['sessions'].append(session)

        # Calculate stats for each game
        stats = []
        for game_type, data in game_data.items():
            game_sessions = data['sessions']
            completed = [s for s in game_sessions if s.completed]

            total_duration = sum(s.duration_seconds or 0 for s in completed)
            completion_rate = (len(completed) / len(game_sessions) * 100) if game_sessions else 0

            mood_improvements = [s.mood_improvement for s in completed if s.mood_improvement is not None]
            avg_mood_improvement = sum(mood_improvements) / len(mood_improvements) if mood_improvements else None

            effectiveness_ratings = [s.effectiveness_rating for s in completed if s.effectiveness_rating]
            avg_effectiveness = sum(effectiveness_ratings) / len(effectiveness_ratings) if effectiveness_ratings else None

            last_played = max((s.started_at for s in game_sessions), default=None)

            stats.append(GameStats(
                game_type=game_type,
                game_name=data['game_name'],
                total_sessions=len(game_sessions),
                total_duration_minutes=total_duration // 60,
                completion_rate=round(completion_rate, 1),
                average_mood_improvement=round(avg_mood_improvement, 2) if avg_mood_improvement else None,
                average_effectiveness=round(avg_effectiveness, 2) if avg_effectiveness else None,
                last_played=last_played
            ))

        return stats

    def get_weekly_activity(self, user_id: int) -> WeeklyActivity:
        """Get activity breakdown by day of week"""
        week_ago = datetime.utcnow() - timedelta(days=7)
        sessions = self.db.query(GameSession)\
            .filter(GameSession.user_id == user_id)\
            .filter(GameSession.started_at >= week_ago)\
            .all()

        # Count by day of week
        day_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        for session in sessions:
            day_of_week = session.started_at.weekday()
            day_counts[day_of_week] += 1

        return WeeklyActivity(
            monday=day_counts[0],
            tuesday=day_counts[1],
            wednesday=day_counts[2],
            thursday=day_counts[3],
            friday=day_counts[4],
            saturday=day_counts[5],
            sunday=day_counts[6],
            total=sum(day_counts.values())
        )

    def get_mood_trends(self, user_id: int) -> MoodTrends:
        """Get mood improvement trends"""
        sessions = self.repo.get_user_sessions(user_id, limit=100)

        sessions_with_mood = [s for s in sessions if s.pre_mood and s.post_mood]

        if not sessions_with_mood:
            return MoodTrends(
                average_pre_mood=None,
                average_post_mood=None,
                average_improvement=None,
                total_sessions_with_mood=0
            )

        avg_pre = sum(s.pre_mood for s in sessions_with_mood) / len(sessions_with_mood)
        avg_post = sum(s.post_mood for s in sessions_with_mood) / len(sessions_with_mood)
        avg_improvement = avg_post - avg_pre

        return MoodTrends(
            average_pre_mood=round(avg_pre, 2),
            average_post_mood=round(avg_post, 2),
            average_improvement=round(avg_improvement, 2),
            total_sessions_with_mood=len(sessions_with_mood)
        )

    def get_achievements(self, user_id: int) -> List[AchievementResponse]:
        """Get user's achievements"""
        achievements = self.repo.get_user_achievements(user_id)
        return [AchievementResponse.model_validate(a) for a in achievements]

    def _check_and_unlock_achievements(self, user_id: int, session: GameSession) -> List[NewAchievementNotification]:
        """Check and unlock any new achievements"""
        new_achievements = []

        # Get current stats
        total_sessions = self.repo.get_completed_sessions(user_id)
        current_streak = self.repo.get_current_streak(user_id)

        # Check session milestones
        session_milestones = [
            (1, "first_session", "First Step", "Started your wellness journey"),
            (5, "sessions_5", "Getting Started", "Completed 5 sessions"),
            (10, "sessions_10", "Building Habits", "Completed 10 sessions"),
            (25, "sessions_25", "Dedicated", "Completed 25 sessions"),
            (50, "sessions_50", "Wellness Warrior", "Completed 50 sessions"),
        ]

        for count, achievement_type, name, description in session_milestones:
            if total_sessions == count:
                existing = self.repo.get_achievement_by_type(user_id, achievement_type)
                if not existing:
                    self.repo.create_achievement(
                        user_id=user_id,
                        achievement_type=achievement_type,
                        achievement_name=name,
                        description=description,
                        icon="trophy",
                        category="activity"
                    )
                    new_achievements.append(NewAchievementNotification(
                        achievement_type=achievement_type,
                        achievement_name=name,
                        achievement_description=description,
                        icon="trophy"
                    ))

        # Check streak achievements
        streak_milestones = [
            (3, "streak_3", "3-Day Streak", "Practiced for 3 days in a row"),
            (7, "streak_7", "Week Warrior", "7-day streak!"),
            (14, "streak_14", "Two Weeks Strong", "14-day streak!"),
            (30, "streak_30", "Monthly Master", "30-day streak!"),
        ]

        for count, achievement_type, name, description in streak_milestones:
            if current_streak == count:
                existing = self.repo.get_achievement_by_type(user_id, achievement_type)
                if not existing:
                    self.repo.create_achievement(
                        user_id=user_id,
                        achievement_type=achievement_type,
                        achievement_name=name,
                        description=description,
                        icon="fire",
                        category="consistency"
                    )
                    new_achievements.append(NewAchievementNotification(
                        achievement_type=achievement_type,
                        achievement_name=name,
                        achievement_description=description,
                        icon="fire"
                    ))

        # Check game-specific milestones
        game_sessions = self.repo.get_sessions_by_game_type(user_id, session.game_type)
        game_count = len([s for s in game_sessions if s.completed])

        game_milestones = [10, 25, 50]
        for count in game_milestones:
            if game_count == count:
                achievement_type = f"{session.game_type}_{count}"
                existing = self.repo.get_achievement_by_type(user_id, achievement_type)
                if not existing:
                    self.repo.create_achievement(
                        user_id=user_id,
                        achievement_type=achievement_type,
                        achievement_name=f"{session.game_name} Expert",
                        description=f"Completed {count} {session.game_name} sessions",
                        icon="star",
                        category="activity"
                    )
                    new_achievements.append(NewAchievementNotification(
                        achievement_type=achievement_type,
                        achievement_name=f"{session.game_name} Expert",
                        achievement_description=f"Completed {count} {session.game_name} sessions",
                        icon="star"
                    ))

        return new_achievements
