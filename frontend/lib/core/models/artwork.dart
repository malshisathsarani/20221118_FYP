class ArtworkModel {
  final int? id;
  final int? userId;
  final String? title;
  final String imageData;
  final String? thumbnailData;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  ArtworkModel({
    this.id,
    this.userId,
    this.title,
    required this.imageData,
    this.thumbnailData,
    this.createdAt,
    this.updatedAt,
  });

  factory ArtworkModel.fromJson(Map<String, dynamic> json) {
    return ArtworkModel(
      id: json['id'] as int?,
      userId: json['user_id'] as int?,
      title: json['title'] as String?,
      imageData: json['image_data'] as String,
      thumbnailData: json['thumbnail_data'] as String?,
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
      if (userId != null) 'user_id': userId,
      if (title != null) 'title': title,
      'image_data': imageData,
      if (thumbnailData != null) 'thumbnail_data': thumbnailData,
    };
  }

  ArtworkModel copyWith({
    int? id,
    int? userId,
    String? title,
    String? imageData,
    String? thumbnailData,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return ArtworkModel(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      title: title ?? this.title,
      imageData: imageData ?? this.imageData,
      thumbnailData: thumbnailData ?? this.thumbnailData,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

class ArtworkThumbnail {
  final int id;
  final String? title;
  final String? thumbnailData;
  final DateTime createdAt;

  ArtworkThumbnail({
    required this.id,
    this.title,
    this.thumbnailData,
    required this.createdAt,
  });

  factory ArtworkThumbnail.fromJson(Map<String, dynamic> json) {
    return ArtworkThumbnail(
      id: json['id'] as int,
      title: json['title'] as String?,
      thumbnailData: json['thumbnail_data'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}
