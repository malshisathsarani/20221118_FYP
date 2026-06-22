import 'package:dio/dio.dart';
import '../network/http_client.dart';
import '../config/api_config.dart';
import '../models/feedback_model.dart';

class FeedbackService {
  final HttpClient _httpClient = HttpClient();

  /// Submit feedback for a chat response
  ///
  /// Parameters:
  /// - chatId: ID of the chat message being reviewed
  /// - rating: 1-5 stars (1 = unhelpful, 5 = very helpful)
  /// - feedbackType: emotion_accuracy | response_quality | crisis_detection
  /// - comment: Optional user comment (max 500 characters)
  Future<FeedbackResponse> submitFeedback({
    required int chatId,
    required int rating,
    required FeedbackType feedbackType,
    String? comment,
  }) async {
    try {
      final response = await _httpClient.dio.post(
        ApiConfig.submitFeedback,
        data: {
          'chat_id': chatId,
          'rating': rating,
          'feedback_type': feedbackType.value,
          if (comment != null && comment.isNotEmpty) 'comment': comment,
        },
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        return FeedbackResponse.fromJson(response.data);
      } else {
        throw Exception('Failed to submit feedback');
      }
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get user's feedback history
  Future<List<FeedbackResponse>> getMyFeedbacks({
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final response = await _httpClient.dio.get(
        ApiConfig.getMyFeedbacks,
        queryParameters: {
          'limit': limit,
          'offset': offset,
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        return data.map((json) => FeedbackResponse.fromJson(json)).toList();
      } else {
        throw Exception('Failed to get feedbacks');
      }
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get bias analysis for user's feedback
  ///
  /// This is a key research feature that analyzes feedback patterns
  /// to detect bias in ML model responses
  Future<BiasAnalysisResult> getBiasAnalysis({int days = 30}) async {
    try {
      final response = await _httpClient.dio.get(
        ApiConfig.getBiasAnalysis,
        queryParameters: {'days': days},
      );

      if (response.statusCode == 200) {
        return BiasAnalysisResult.fromJson(response.data);
      } else {
        throw Exception('Failed to get bias analysis');
      }
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get aggregated feedback statistics
  Future<FeedbackStats> getFeedbackStats() async {
    try {
      final response = await _httpClient.dio.get(ApiConfig.getFeedbackStats);

      if (response.statusCode == 200) {
        return FeedbackStats.fromJson(response.data);
      } else {
        throw Exception('Failed to get feedback stats');
      }
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Exception _handleError(DioException e) {
    if (e.response != null) {
      final detail = e.response?.data['detail'];
      return Exception(detail ?? 'Feedback operation failed');
    } else {
      return Exception('Network error: ${e.message}');
    }
  }
}
