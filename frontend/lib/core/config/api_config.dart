class ApiConfig {
  // Base URL - Change this to your backend URL
  static const String baseUrl = 'http://localhost:8000';

  // API Endpoints
  static const String apiPrefix = '/api';

  // Auth endpoints
  static const String register = '$apiPrefix/auth/register';
  static const String login = '$apiPrefix/auth/login';
  static const String refreshToken = '$apiPrefix/auth/refresh';

  // Chat endpoints
  static const String createChat = '$apiPrefix/chat/create';
  static String sendMessage(String sessionId) => '$apiPrefix/chat/$sessionId/message';
  static String getChatHistory(String sessionId) => '$apiPrefix/chat/$sessionId/messages';
  static const String getMyChats = '$apiPrefix/chat/my-chats';

  // Crisis endpoints
  static const String crisisAlerts = '$apiPrefix/crisis/alerts';
  static const String crisisResources = '$apiPrefix/crisis/resources';

  // Audio endpoints
  static const String uploadAudio = '$apiPrefix/audio/upload';
  static String deleteAudio(String audioId) => '$apiPrefix/audio/delete/$audioId';

  // Profile endpoints
  static const String getProfile = '$apiPrefix/profile/me';
  static const String updateProfile = '$apiPrefix/profile/me';
  static const String getPreferences = '$apiPrefix/profile/me/preferences';
  static const String updatePreferences = '$apiPrefix/profile/me/preferences';
  static const String getPrivacySettings = '$apiPrefix/profile/me/privacy';
  static const String updatePrivacySettings = '$apiPrefix/profile/me/privacy';
  static const String deleteAvatar = '$apiPrefix/profile/me/avatar';
  static const String getInitials = '$apiPrefix/profile/me/initials';

  // Timeouts
  static const Duration connectionTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
}
