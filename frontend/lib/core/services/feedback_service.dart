import 'package:dio/dio.dart';
import '../network/http_client.dart';
import '../config/api_config.dart';

class FeedbackService {
  final HttpClient _httpClient = HttpClient();

  /// Submit feedback for a chat message
  ///
  /// [chatId] - The ID of the chat message being rated
  /// [rating] - Rating from 1 (very poor) to 5 (excellent)
  /// [feedbackType] - Type of feedback: 'emotion_accuracy', 'response_quality', 'crisis_detection', 'bias_report'
  /// [comment] - Optional text explanation
  Future<Map<String, dynamic>> submitFeedback({
    int? chatId,
    required int rating,
    required String feedbackType,
    String? comment,
  }) async {
    try {
      final response = await _httpClient.dio.post(
        '${ApiConfig.baseUrl}${ApiConfig.apiPrefix}/feedback/',
        data: {
          if (chatId != null) 'chat_id': chatId,
          'rating': rating,
          'feedback_type': feedbackType,
          if (comment != null && comment.isNotEmpty) 'comment': comment,
        },
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        return response.data;
      } else {
        throw Exception('Failed to submit feedback');
      }
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get all feedback submitted by the current user
  Future<List<Map<String, dynamic>>> getMyFeedback({
    int limit = 50,
    String? feedbackType,
  }) async {
    try {
      final response = await _httpClient.dio.get(
        '${ApiConfig.baseUrl}${ApiConfig.apiPrefix}/feedback/my-feedback',
        queryParameters: {
          'limit': limit,
          if (feedbackType != null) 'feedback_type': feedbackType,
        },
      );

      if (response.statusCode == 200) {
        return List<Map<String, dynamic>>.from(response.data);
      } else {
        throw Exception('Failed to get feedback');
      }
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get feedback statistics
  Future<Map<String, dynamic>> getFeedbackStats({
    String? feedbackType,
    int days = 30,
  }) async {
    try {
      final response = await _httpClient.dio.get(
        '${ApiConfig.baseUrl}${ApiConfig.apiPrefix}/feedback/stats',
        queryParameters: {
          if (feedbackType != null) 'feedback_type': feedbackType,
          'days': days,
        },
      );

      if (response.statusCode == 200) {
        return response.data;
      } else {
        throw Exception('Failed to get feedback stats');
      }
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get emotion accuracy analysis
  Future<Map<String, dynamic>> getEmotionAccuracyAnalysis({
    int days = 30,
  }) async {
    try {
      final response = await _httpClient.dio.get(
        '${ApiConfig.baseUrl}${ApiConfig.apiPrefix}/feedback/analysis/emotion-accuracy',
        queryParameters: {
          'days': days,
        },
      );

      if (response.statusCode == 200) {
        return response.data;
      } else {
        throw Exception('Failed to get emotion accuracy analysis');
      }
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get bias report
  Future<Map<String, dynamic>> getBiasReport({
    int days = 30,
  }) async {
    try {
      final response = await _httpClient.dio.get(
        '${ApiConfig.baseUrl}${ApiConfig.apiPrefix}/feedback/bias-report',
        queryParameters: {
          'days': days,
        },
      );

      if (response.statusCode == 200) {
        return response.data;
      } else {
        throw Exception('Failed to get bias report');
      }
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Exception _handleError(DioException e) {
    if (e.response != null) {
      final statusCode = e.response!.statusCode;
      final message = e.response!.data['detail'] ?? 'Unknown error occurred';

      switch (statusCode) {
        case 400:
          return Exception('Bad request: $message');
        case 401:
          return Exception('Unauthorized: Please log in again');
        case 403:
          return Exception('Forbidden: $message');
        case 404:
          return Exception('Not found: $message');
        case 500:
          return Exception('Server error: $message');
        default:
          return Exception('Error: $message');
      }
    } else if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.receiveTimeout) {
      return Exception('Connection timeout. Please check your internet connection.');
    } else if (e.type == DioExceptionType.connectionError) {
      return Exception('No internet connection. Please check your network.');
    } else {
      return Exception('An unexpected error occurred: ${e.message}');
    }
  }
}
