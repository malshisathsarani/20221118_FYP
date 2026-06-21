import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:dio/dio.dart';
import 'package:http_parser/http_parser.dart';
import 'package:universal_html/html.dart' as html;
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
    String? audioPath,
  }) async {
    try {
      String? audioUrl;

      // Step 1: Upload audio if provided
      if (audioPath != null && audioPath.isNotEmpty) {
        audioUrl = await _uploadAudio(audioPath);
      }

      // Step 2: Send message with optional audio URL
      final response = await _httpClient.dio.post(
        ApiConfig.sendMessage(sessionId),
        data: {
          'message': message,
          'session_id': sessionId,
          if (audioUrl != null) 'audio_data': audioUrl,
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

  /// Upload audio file to server and return the URL
  Future<String> _uploadAudio(String audioPath) async {
    try {
      FormData formData;

      if (kIsWeb) {
        // For web, audioPath is a blob URL
        // We need to fetch the blob and convert it to bytes
        final response = await html.window.fetch(audioPath);
        final blob = await response.blob();
        final bytes = await _readBlobAsBytes(blob);

        final fileName = 'audio_${DateTime.now().millisecondsSinceEpoch}.wav';

        formData = FormData.fromMap({
          'file': MultipartFile.fromBytes(
            bytes,
            filename: fileName,
            contentType: MediaType('audio', 'wav'),
          ),
        });
      } else {
        // For mobile, use file path
        final fileName = audioPath.split('/').last;
        formData = FormData.fromMap({
          'file': await MultipartFile.fromFile(
            audioPath,
            filename: fileName,
            contentType: MediaType('audio', 'wav'),
          ),
        });
      }

      // Upload to audio endpoint
      final uploadResponse = await _httpClient.dio.post(
        ApiConfig.uploadAudio,
        data: formData,
        options: Options(
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        ),
      );

      if (uploadResponse.statusCode == 200) {
        // Return the audio URL from Cloudinary
        return uploadResponse.data['audio_path'];
      } else {
        throw Exception('Failed to upload audio');
      }
    } on DioException catch (e) {
      throw _handleError(e);
    } catch (e) {
      throw 'Failed to upload audio: $e';
    }
  }

  /// Helper to read blob as bytes (web only)
  Future<List<int>> _readBlobAsBytes(html.Blob blob) async {
    final reader = html.FileReader();
    reader.readAsArrayBuffer(blob);
    await reader.onLoad.first;
    final result = reader.result as List<int>;
    return result;
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
