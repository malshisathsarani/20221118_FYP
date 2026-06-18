import 'package:dio/dio.dart';
import '../network/http_client.dart';
import '../config/api_config.dart';
import '../models/game_tracking_model.dart';

class GameTrackingService {
  final HttpClient _httpClient = HttpClient();

  /// Get progress summary
  Future<ProgressSummary> getProgressSummary() async {
    try {
      final response = await _httpClient.dio.get(
        '${ApiConfig.apiPrefix}/games/progress/summary',
      );

      if (response.statusCode == 200) {
        return ProgressSummary.fromJson(response.data);
      } else {
        throw Exception('Failed to fetch progress summary');
      }
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Start a game session
  Future<GameSession> startSession(GameSessionStart sessionData) async {
    try {
      final response = await _httpClient.dio.post(
        '${ApiConfig.apiPrefix}/games/sessions/start',
        data: sessionData.toJson(),
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        return GameSession.fromJson(response.data);
      } else {
        throw Exception('Failed to start session');
      }
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Complete a game session
  Future<SessionCompleteResponse> completeSession(
    int sessionId,
    GameSessionComplete completionData,
  ) async {
    try {
      final response = await _httpClient.dio.put(
        '${ApiConfig.apiPrefix}/games/sessions/$sessionId/complete',
        data: completionData.toJson(),
      );

      if (response.statusCode == 200) {
        return SessionCompleteResponse.fromJson(response.data);
      } else {
        throw Exception('Failed to complete session');
      }
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get weekly activity
  Future<WeeklyActivity> getWeeklyActivity() async {
    try {
      final response = await _httpClient.dio.get(
        '${ApiConfig.apiPrefix}/games/stats/weekly',
      );

      if (response.statusCode == 200) {
        return WeeklyActivity.fromJson(response.data);
      } else {
        throw Exception('Failed to fetch weekly activity');
      }
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  String _handleError(DioException error) {
    if (error.response != null) {
      final data = error.response!.data;
      if (data is Map && data.containsKey('detail')) {
        return data['detail'].toString();
      }
      return 'Server error: ${error.response!.statusCode}';
    } else {
      return 'Network error. Please check your connection.';
    }
  }
}
