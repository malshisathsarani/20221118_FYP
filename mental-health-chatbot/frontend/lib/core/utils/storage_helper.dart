import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../constants/app_constants.dart';

class StorageHelper {
  static final _prefs = SharedPreferences.getInstance();
  static const _secureStorage = FlutterSecureStorage();

  // Secure storage for tokens
  static Future<void> saveAccessToken(String token) async {
    await _secureStorage.write(key: AppConstants.keyAccessToken, value: token);
  }

  static Future<String?> getAccessToken() async {
    return await _secureStorage.read(key: AppConstants.keyAccessToken);
  }

  static Future<void> saveRefreshToken(String token) async {
    await _secureStorage.write(key: AppConstants.keyRefreshToken, value: token);
  }

  static Future<String?> getRefreshToken() async {
    return await _secureStorage.read(key: AppConstants.keyRefreshToken);
  }

  // Regular storage for user info
  static Future<void> saveUserId(int userId) async {
    final prefs = await _prefs;
    await prefs.setInt(AppConstants.keyUserId, userId);
  }

  static Future<int?> getUserId() async {
    final prefs = await _prefs;
    return prefs.getInt(AppConstants.keyUserId);
  }

  static Future<void> saveUserEmail(String email) async {
    final prefs = await _prefs;
    await prefs.setString(AppConstants.keyUserEmail, email);
  }

  static Future<String?> getUserEmail() async {
    final prefs = await _prefs;
    return prefs.getString(AppConstants.keyUserEmail);
  }

  static Future<void> setLoggedIn(bool value) async {
    final prefs = await _prefs;
    await prefs.setBool(AppConstants.keyIsLoggedIn, value);
  }

  static Future<bool> isLoggedIn() async {
    final prefs = await _prefs;
    return prefs.getBool(AppConstants.keyIsLoggedIn) ?? false;
  }

  static Future<void> setHasSeenOnboarding(bool value) async {
    final prefs = await _prefs;
    await prefs.setBool(AppConstants.keyHasSeenOnboarding, value);
  }

  static Future<bool> hasSeenOnboarding() async {
    final prefs = await _prefs;
    return prefs.getBool(AppConstants.keyHasSeenOnboarding) ?? false;
  }

  // Clear all data
  static Future<void> clearAll() async {
    final prefs = await _prefs;
    await prefs.clear();
    await _secureStorage.deleteAll();
  }
}
