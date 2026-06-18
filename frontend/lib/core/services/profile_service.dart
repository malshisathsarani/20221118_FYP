import 'package:dio/dio.dart';
import '../network/http_client.dart';
import '../config/api_config.dart';
import '../models/profile_model.dart';

class ProfileService {
  final HttpClient _httpClient = HttpClient();

  /// Get current user's profile
  Future<ProfileModel> getProfile() async {
    try {
      final response = await _httpClient.dio.get(ApiConfig.getProfile);

      if (response.statusCode == 200) {
        return ProfileModel.fromJson(response.data);
      } else {
        throw Exception('Failed to fetch profile');
      }
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Update profile information
  Future<ProfileModel> updateProfile(ProfileUpdateRequest updateData) async {
    try {
      final response = await _httpClient.dio.put(
        ApiConfig.updateProfile,
        data: updateData.toJson(),
      );

      if (response.statusCode == 200) {
        return ProfileModel.fromJson(response.data);
      } else {
        throw Exception('Failed to update profile');
      }
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Update notification preferences
  Future<ProfileModel> updatePreferences(PreferencesUpdateRequest preferencesData) async {
    try {
      final response = await _httpClient.dio.put(
        ApiConfig.updatePreferences,
        data: preferencesData.toJson(),
      );

      if (response.statusCode == 200) {
        return ProfileModel.fromJson(response.data);
      } else {
        throw Exception('Failed to update preferences');
      }
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Update privacy settings
  Future<ProfileModel> updatePrivacySettings(PrivacySettingsUpdateRequest privacyData) async {
    try {
      final response = await _httpClient.dio.put(
        ApiConfig.updatePrivacySettings,
        data: privacyData.toJson(),
      );

      if (response.statusCode == 200) {
        return ProfileModel.fromJson(response.data);
      } else {
        throw Exception('Failed to update privacy settings');
      }
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Delete user avatar
  Future<ProfileModel> deleteAvatar() async {
    try {
      final response = await _httpClient.dio.delete(ApiConfig.deleteAvatar);

      if (response.statusCode == 200) {
        return ProfileModel.fromJson(response.data);
      } else {
        throw Exception('Failed to delete avatar');
      }
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get user initials for avatar display
  Future<String> getInitials() async {
    try {
      final response = await _httpClient.dio.get(ApiConfig.getInitials);

      if (response.statusCode == 200) {
        return response.data['initials'] as String;
      } else {
        throw Exception('Failed to get initials');
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
