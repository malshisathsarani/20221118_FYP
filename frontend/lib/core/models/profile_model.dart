class ProfileModel {
  final int id;
  final String email;
  final String username;
  final String? fullName;
  final String? phoneNumber;
  final String? bio;
  final String? avatarUrl;
  final bool isActive;
  final bool isVerified;
  final DateTime createdAt;
  final DateTime updatedAt;

  // Preferences
  final bool notificationsEnabled;
  final bool emailNotifications;

  // Privacy settings
  final bool dataSharingConsent;
  final bool analyticsConsent;

  ProfileModel({
    required this.id,
    required this.email,
    required this.username,
    this.fullName,
    this.phoneNumber,
    this.bio,
    this.avatarUrl,
    required this.isActive,
    required this.isVerified,
    required this.createdAt,
    required this.updatedAt,
    required this.notificationsEnabled,
    required this.emailNotifications,
    required this.dataSharingConsent,
    required this.analyticsConsent,
  });

  factory ProfileModel.fromJson(Map<String, dynamic> json) {
    return ProfileModel(
      id: json['id'],
      email: json['email'],
      username: json['username'],
      fullName: json['full_name'],
      phoneNumber: json['phone_number'],
      bio: json['bio'],
      avatarUrl: json['avatar_url'],
      isActive: json['is_active'] ?? true,
      isVerified: json['is_verified'] ?? false,
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
      notificationsEnabled: json['notifications_enabled'] ?? true,
      emailNotifications: json['email_notifications'] ?? true,
      dataSharingConsent: json['data_sharing_consent'] ?? false,
      analyticsConsent: json['analytics_consent'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'username': username,
      'full_name': fullName,
      'phone_number': phoneNumber,
      'bio': bio,
      'avatar_url': avatarUrl,
      'is_active': isActive,
      'is_verified': isVerified,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'notifications_enabled': notificationsEnabled,
      'email_notifications': emailNotifications,
      'data_sharing_consent': dataSharingConsent,
      'analytics_consent': analyticsConsent,
    };
  }

  String getInitials() {
    if (fullName != null && fullName!.isNotEmpty) {
      final names = fullName!.split(' ');
      if (names.length >= 2) {
        return '${names[0][0]}${names[names.length - 1][0]}'.toUpperCase();
      } else if (names.length == 1) {
        return names[0].substring(0, names[0].length >= 2 ? 2 : 1).toUpperCase();
      }
    }
    // Fallback to username
    return username.substring(0, username.length >= 2 ? 2 : 1).toUpperCase();
  }

  ProfileModel copyWith({
    int? id,
    String? email,
    String? username,
    String? fullName,
    String? phoneNumber,
    String? bio,
    String? avatarUrl,
    bool? isActive,
    bool? isVerified,
    DateTime? createdAt,
    DateTime? updatedAt,
    bool? notificationsEnabled,
    bool? emailNotifications,
    bool? dataSharingConsent,
    bool? analyticsConsent,
  }) {
    return ProfileModel(
      id: id ?? this.id,
      email: email ?? this.email,
      username: username ?? this.username,
      fullName: fullName ?? this.fullName,
      phoneNumber: phoneNumber ?? this.phoneNumber,
      bio: bio ?? this.bio,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      isActive: isActive ?? this.isActive,
      isVerified: isVerified ?? this.isVerified,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      notificationsEnabled: notificationsEnabled ?? this.notificationsEnabled,
      emailNotifications: emailNotifications ?? this.emailNotifications,
      dataSharingConsent: dataSharingConsent ?? this.dataSharingConsent,
      analyticsConsent: analyticsConsent ?? this.analyticsConsent,
    );
  }
}

class ProfileUpdateRequest {
  final String? fullName;
  final String? phoneNumber;
  final String? bio;
  final String? avatarUrl;

  ProfileUpdateRequest({
    this.fullName,
    this.phoneNumber,
    this.bio,
    this.avatarUrl,
  });

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = {};
    if (fullName != null) data['full_name'] = fullName;
    if (phoneNumber != null) data['phone_number'] = phoneNumber;
    if (bio != null) data['bio'] = bio;
    if (avatarUrl != null) data['avatar_url'] = avatarUrl;
    return data;
  }
}

class PreferencesUpdateRequest {
  final bool? notificationsEnabled;
  final bool? emailNotifications;

  PreferencesUpdateRequest({
    this.notificationsEnabled,
    this.emailNotifications,
  });

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = {};
    if (notificationsEnabled != null) data['notifications_enabled'] = notificationsEnabled;
    if (emailNotifications != null) data['email_notifications'] = emailNotifications;
    return data;
  }
}

class PrivacySettingsUpdateRequest {
  final bool? dataSharingConsent;
  final bool? analyticsConsent;

  PrivacySettingsUpdateRequest({
    this.dataSharingConsent,
    this.analyticsConsent,
  });

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = {};
    if (dataSharingConsent != null) data['data_sharing_consent'] = dataSharingConsent;
    if (analyticsConsent != null) data['analytics_consent'] = analyticsConsent;
    return data;
  }
}
