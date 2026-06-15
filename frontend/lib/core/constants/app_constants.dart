class AppConstants {
  // App Info
  static const String appName = 'Mental Health Chatbot';
  static const String appVersion = '1.0.0';

  // Storage Keys
  static const String keyAccessToken = 'access_token';
  static const String keyRefreshToken = 'refresh_token';
  static const String keyUserId = 'user_id';
  static const String keyUserEmail = 'user_email';
  static const String keyIsLoggedIn = 'is_logged_in';
  static const String keyHasSeenOnboarding = 'has_seen_onboarding';

  // Emergency Contacts
  static const String emergencyHotline = '988';
  static const String crisisTextLine = '741741';

  // Validation
  static const int minPasswordLength = 8;
  static const int maxMessageLength = 1000;

  // UI
  static const double defaultPadding = 16.0;
  static const double defaultBorderRadius = 12.0;
}
