class EmergencyContactModel {
  final int? id;
  final String name;
  final String phone;
  final String? relationshipType;
  final String? email;
  final bool isPrimary;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  EmergencyContactModel({
    this.id,
    required this.name,
    required this.phone,
    this.relationshipType,
    this.email,
    this.isPrimary = false,
    this.createdAt,
    this.updatedAt,
  });

  factory EmergencyContactModel.fromJson(Map<String, dynamic> json) {
    return EmergencyContactModel(
      id: json['id'] as int?,
      name: json['name'] as String,
      phone: json['phone'] as String,
      relationshipType: json['relationship_type'] as String?,
      email: json['email'] as String?,
      isPrimary: (json['is_primary'] as int?) == 1,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : null,
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'name': name,
      'phone': phone,
      if (relationshipType != null) 'relationship_type': relationshipType,
      if (email != null) 'email': email,
      'is_primary': isPrimary ? 1 : 0,
    };
  }

  EmergencyContactModel copyWith({
    int? id,
    String? name,
    String? phone,
    String? relationshipType,
    String? email,
    bool? isPrimary,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return EmergencyContactModel(
      id: id ?? this.id,
      name: name ?? this.name,
      phone: phone ?? this.phone,
      relationshipType: relationshipType ?? this.relationshipType,
      email: email ?? this.email,
      isPrimary: isPrimary ?? this.isPrimary,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
