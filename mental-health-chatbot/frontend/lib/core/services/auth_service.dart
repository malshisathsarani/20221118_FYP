import 'package:dio/dio.dart';
import '../network/http_client.dart';
import '../config/api_config.dart';
import '../models/user_model.dart';
import '../utils/storage_helper.dart';

class AuthService {
  final HttpClient _httpClient = HttpClient();

  Future<AuthResponse> register({
    required String email,
    required String username,
    required String password,
    String? fullName,
  }) async {
    try {
      final response = await _httpClient.dio.post(
        ApiConfig.register,
        data: {
          'email': email,
          'username': username,
          'password': password,
          'full_name': fullName,
        },
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        // Auto login after registration
        return await login(email: email, password: password);
      } else {
        throw Exception('Registration failed');
      }
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<AuthResponse> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await _httpClient.dio.post(
        ApiConfig.login,
        data: {
          'email': email,
          'password': password,
        },
      );

      if (response.statusCode == 200) {
        final authResponse = AuthResponse.fromJson(response.data);

        // Save tokens
        await StorageHelper.saveAccessToken(authResponse.accessToken);
        await StorageHelper.saveRefreshToken(authResponse.refreshToken);
        await StorageHelper.saveUserEmail(email);
        await StorageHelper.setLoggedIn(true);

        return authResponse;
      } else {
        throw Exception('Login failed');
      }
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> logout() async {
    await StorageHelper.clearAll();
  }

  Future<bool> isAuthenticated() async {
    return await StorageHelper.isLoggedIn();
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
