import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../utils/storage_helper.dart';

class UserService {
  final String baseUrl = ApiConfig.baseUrl;

  /// Get current user profile
  Future<Map<String, dynamic>> getCurrentUser() async {
    try {
      final token = await StorageHelper.getAccessToken();

      if (token == null) {
        throw Exception('No access token found');
      }

      final response = await http.get(
        Uri.parse('$baseUrl/api/auth/me'),
        headers: {
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to load user profile');
      }
    } catch (e) {
      throw Exception('Error fetching user: ${e.toString()}');
    }
  }

  /// Update user profile
  Future<Map<String, dynamic>> updateProfile({
    String? fullName,
    String? email,
  }) async {
    try {
      final token = await StorageHelper.getAccessToken();

      if (token == null) {
        throw Exception('No access token found');
      }

      final response = await http.put(
        Uri.parse('$baseUrl/api/users/profile'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({
          if (fullName != null) 'full_name': fullName,
          if (email != null) 'email': email,
        }),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to update profile');
      }
    } catch (e) {
      throw Exception('Error updating profile: ${e.toString()}');
    }
  }

  /// Update user preferences
  Future<void> updatePreferences({
    bool? notifications,
    bool? darkMode,
  }) async {
    try {
      final token = await StorageHelper.getAccessToken();

      if (token == null) {
        throw Exception('No access token found');
      }

      final response = await http.put(
        Uri.parse('$baseUrl/api/users/preferences'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({
          if (notifications != null) 'notifications_enabled': notifications,
          if (darkMode != null) 'dark_mode': darkMode,
        }),
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to update preferences');
      }
    } catch (e) {
      throw Exception('Error updating preferences: ${e.toString()}');
    }
  }

  /// Get user statistics for profile
  Future<Map<String, dynamic>> getUserStats() async {
    try {
      final token = await StorageHelper.getAccessToken();

      if (token == null) {
        throw Exception('No access token found');
      }

      final response = await http.get(
        Uri.parse('$baseUrl/api/users/stats'),
        headers: {
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        return {
          'total_chats': 0,
          'crisis_events': 0,
          'tools_used': 0,
          'days_active': 0,
        };
      }
    } catch (e) {
      return {
        'total_chats': 0,
        'crisis_events': 0,
        'tools_used': 0,
        'days_active': 0,
      };
    }
  }

  /// Export user data (GDPR compliance)
  Future<Map<String, dynamic>> exportUserData() async {
    try {
      final token = await StorageHelper.getAccessToken();

      if (token == null) {
        throw Exception('No access token found');
      }

      final response = await http.get(
        Uri.parse('$baseUrl/api/users/export-data'),
        headers: {
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to export data');
      }
    } catch (e) {
      throw Exception('Error exporting data: ${e.toString()}');
    }
  }

  /// Delete account
  Future<void> deleteAccount() async {
    try {
      final token = await StorageHelper.getAccessToken();

      if (token == null) {
        throw Exception('No access token found');
      }

      final response = await http.delete(
        Uri.parse('$baseUrl/api/users/delete-account'),
        headers: {
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to delete account');
      }
    } catch (e) {
      throw Exception('Error deleting account: ${e.toString()}');
    }
  }

  /// Logout
  Future<void> logout() async {
    await StorageHelper.clearAll();
  }
}
