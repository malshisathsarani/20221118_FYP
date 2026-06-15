import 'package:dio/dio.dart';
import '../network/http_client.dart';
import '../config/api_config.dart';
import '../models/chat_model.dart';

class ChatService {
  final HttpClient _httpClient = HttpClient();

  Future<String> createSession() async {
    try {
      final response = await _httpClient.dio.post(ApiConfig.createChat);

      if (response.statusCode == 201 || response.statusCode == 200) {
        return response.data['session_id'];
      } else {
        throw Exception('Failed to create session');
      }
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<ChatMessage> sendMessage({
    required String sessionId,
    required String message,
    String? audioData,
  }) async {
    try {
      final response = await _httpClient.dio.post(
        ApiConfig.sendMessage(sessionId),
        data: {
          'message': message,
          'session_id': sessionId,
          if (audioData != null) 'audio_data': audioData,
        },
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        return ChatMessage.fromJson(response.data);
      } else {
        throw Exception('Failed to send message');
      }
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<List<ChatMessage>> getChatHistory({
    required String sessionId,
    int limit = 50,
  }) async {
    try {
      final response = await _httpClient.dio.get(
        ApiConfig.getChatHistory(sessionId),
        queryParameters: {'limit': limit},
      );

      if (response.statusCode == 200) {
        final List<dynamic> chats = response.data['chats'];
        return chats.map((chat) => ChatMessage.fromJson(chat)).toList();
      } else {
        throw Exception('Failed to get chat history');
      }
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<List<Map<String, dynamic>>> getMySessions() async {
    try {
      final response = await _httpClient.dio.get(ApiConfig.getMyChats);

      if (response.statusCode == 200) {
        return List<Map<String, dynamic>>.from(response.data['sessions']);
      } else {
        throw Exception('Failed to get sessions');
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
