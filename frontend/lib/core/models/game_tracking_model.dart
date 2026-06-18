class ProgressSummary {
  final int totalSessions;
  final int totalDurationMinutes;
  final int currentStreakDays;
  final int longestStreakDays;
  final int weeklySessions;
  final int monthlySessions;
  final String? favoriteGame;
  final int totalGamesCompleted;
  final double? averageMoodImprovement;
  final int achievementsUnlocked;

  ProgressSummary({
    required this.totalSessions,
    required this.totalDurationMinutes,
    required this.currentStreakDays,
    required this.longestStreakDays,
    required this.weeklySessions,
    required this.monthlySessions,
    this.favoriteGame,
    required this.totalGamesCompleted,
    this.averageMoodImprovement,
    required this.achievementsUnlocked,
  });

  factory ProgressSummary.fromJson(Map<String, dynamic> json) {
    return ProgressSummary(
      totalSessions: json['total_sessions'] ?? 0,
      totalDurationMinutes: json['total_duration_minutes'] ?? 0,
      currentStreakDays: json['current_streak_days'] ?? 0,
      longestStreakDays: json['longest_streak_days'] ?? 0,
      weeklySessions: json['weekly_sessions'] ?? 0,
      monthlySessions: json['monthly_sessions'] ?? 0,
      favoriteGame: json['favorite_game'],
      totalGamesCompleted: json['total_games_completed'] ?? 0,
      averageMoodImprovement: json['average_mood_improvement']?.toDouble(),
      achievementsUnlocked: json['achievements_unlocked'] ?? 0,
    );
  }

  String get formattedDuration {
    final hours = totalDurationMinutes ~/ 60;
    final minutes = totalDurationMinutes % 60;
    if (hours > 0) {
      return '${hours}h ${minutes}min';
    }
    return '${minutes}min';
  }
}

class GameSessionStart {
  final String gameType;
  final String gameName;
  final int? preMood;
  final String? device;

  GameSessionStart({
    required this.gameType,
    required this.gameName,
    this.preMood,
    this.device,
  });

  Map<String, dynamic> toJson() {
    return {
      'game_type': gameType,
      'game_name': gameName,
      if (preMood != null) 'pre_mood': preMood,
      if (device != null) 'device': device,
    };
  }
}

class GameSessionComplete {
  final int? postMood;
  final int? effectivenessRating;
  final String? notes;

  GameSessionComplete({
    this.postMood,
    this.effectivenessRating,
    this.notes,
  });

  Map<String, dynamic> toJson() {
    return {
      if (postMood != null) 'post_mood': postMood,
      if (effectivenessRating != null) 'effectiveness_rating': effectivenessRating,
      if (notes != null) 'notes': notes,
    };
  }
}

class GameSession {
  final int id;
  final String gameType;
  final String gameName;
  final DateTime startedAt;
  final DateTime? completedAt;
  final int? durationSeconds;
  final bool completed;
  final int? preMood;
  final int? postMood;
  final double? moodImprovement;

  GameSession({
    required this.id,
    required this.gameType,
    required this.gameName,
    required this.startedAt,
    this.completedAt,
    this.durationSeconds,
    required this.completed,
    this.preMood,
    this.postMood,
    this.moodImprovement,
  });

  factory GameSession.fromJson(Map<String, dynamic> json) {
    return GameSession(
      id: json['id'],
      gameType: json['game_type'],
      gameName: json['game_name'],
      startedAt: DateTime.parse(json['started_at']),
      completedAt: json['completed_at'] != null
          ? DateTime.parse(json['completed_at'])
          : null,
      durationSeconds: json['duration_seconds'],
      completed: json['completed'] ?? false,
      preMood: json['pre_mood'],
      postMood: json['post_mood'],
      moodImprovement: json['mood_improvement']?.toDouble(),
    );
  }
}

class SessionCompleteResponse {
  final GameSession session;
  final List<Achievement> newAchievements;
  final int currentStreak;
  final int totalSessions;
  final String progressMessage;

  SessionCompleteResponse({
    required this.session,
    required this.newAchievements,
    required this.currentStreak,
    required this.totalSessions,
    required this.progressMessage,
  });

  factory SessionCompleteResponse.fromJson(Map<String, dynamic> json) {
    return SessionCompleteResponse(
      session: GameSession.fromJson(json['session']),
      newAchievements: (json['new_achievements'] as List)
          .map((a) => Achievement.fromJson(a))
          .toList(),
      currentStreak: json['current_streak'],
      totalSessions: json['total_sessions'],
      progressMessage: json['progress_message'],
    );
  }
}

class Achievement {
  final String achievementType;
  final String achievementName;
  final String? achievementDescription;
  final String? icon;

  Achievement({
    required this.achievementType,
    required this.achievementName,
    this.achievementDescription,
    this.icon,
  });

  factory Achievement.fromJson(Map<String, dynamic> json) {
    return Achievement(
      achievementType: json['achievement_type'],
      achievementName: json['achievement_name'],
      achievementDescription: json['achievement_description'],
      icon: json['icon'],
    );
  }
}

class WeeklyActivity {
  final int monday;
  final int tuesday;
  final int wednesday;
  final int thursday;
  final int friday;
  final int saturday;
  final int sunday;
  final int total;

  WeeklyActivity({
    required this.monday,
    required this.tuesday,
    required this.wednesday,
    required this.thursday,
    required this.friday,
    required this.saturday,
    required this.sunday,
    required this.total,
  });

  factory WeeklyActivity.fromJson(Map<String, dynamic> json) {
    return WeeklyActivity(
      monday: json['monday'] ?? 0,
      tuesday: json['tuesday'] ?? 0,
      wednesday: json['wednesday'] ?? 0,
      thursday: json['thursday'] ?? 0,
      friday: json['friday'] ?? 0,
      saturday: json['saturday'] ?? 0,
      sunday: json['sunday'] ?? 0,
      total: json['total'] ?? 0,
    );
  }

  int get maxSessions {
    return [monday, tuesday, wednesday, thursday, friday, saturday, sunday]
        .reduce((a, b) => a > b ? a : b);
  }
}
