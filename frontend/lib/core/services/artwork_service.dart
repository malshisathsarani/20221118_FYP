import 'package:dio/dio.dart';
import '../network/http_client.dart';
import '../models/artwork.dart';

class ArtworkService {
  final HttpClient _httpClient = HttpClient();

  /// Create a new artwork
  Future<ArtworkModel> createArtwork({
    required String imageData,
    String? title,
    String? thumbnailData,
  }) async {
    try {
      final response = await _httpClient.dio.post(
        '/api/artworks/',
        data: {
          'image_data': imageData,
          if (title != null) 'title': title,
          if (thumbnailData != null) 'thumbnail_data': thumbnailData,
        },
      );

      if (response.statusCode == 201) {
        return ArtworkModel.fromJson(response.data);
      } else {
        throw Exception('Failed to create artwork: ${response.statusCode}');
      }
    } on DioException catch (e) {
      throw Exception('Error creating artwork: ${e.message}');
    }
  }

  /// Get all artworks for the current user
  Future<List<ArtworkModel>> getArtworks({int skip = 0, int limit = 100}) async {
    try {
      final response = await _httpClient.dio.get(
        '/api/artworks/',
        queryParameters: {
          'skip': skip,
          'limit': limit,
        },
      );

      if (response.statusCode == 200) {
        final List artworksJson = response.data['artworks'] as List;
        return artworksJson
            .map((json) => ArtworkModel.fromJson(json))
            .toList();
      } else {
        throw Exception('Failed to load artworks: ${response.statusCode}');
      }
    } on DioException catch (e) {
      throw Exception('Error loading artworks: ${e.message}');
    }
  }

  /// Get artwork thumbnails for gallery view
  Future<List<ArtworkThumbnail>> getThumbnails({int skip = 0, int limit = 50}) async {
    try {
      final response = await _httpClient.dio.get(
        '/api/artworks/thumbnails',
        queryParameters: {
          'skip': skip,
          'limit': limit,
        },
      );

      if (response.statusCode == 200) {
        final List thumbnailsJson = response.data as List;
        return thumbnailsJson
            .map((json) => ArtworkThumbnail.fromJson(json))
            .toList();
      } else {
        throw Exception('Failed to load thumbnails: ${response.statusCode}');
      }
    } on DioException catch (e) {
      throw Exception('Error loading thumbnails: ${e.message}');
    }
  }

  /// Get a specific artwork by ID
  Future<ArtworkModel> getArtwork(int artworkId) async {
    try {
      final response = await _httpClient.dio.get('/api/artworks/$artworkId');

      if (response.statusCode == 200) {
        return ArtworkModel.fromJson(response.data);
      } else {
        throw Exception('Failed to load artwork: ${response.statusCode}');
      }
    } on DioException catch (e) {
      throw Exception('Error loading artwork: ${e.message}');
    }
  }

  /// Update artwork (only title)
  Future<ArtworkModel> updateArtwork(int artworkId, {String? title}) async {
    try {
      final response = await _httpClient.dio.put(
        '/api/artworks/$artworkId',
        data: {
          if (title != null) 'title': title,
        },
      );

      if (response.statusCode == 200) {
        return ArtworkModel.fromJson(response.data);
      } else {
        throw Exception('Failed to update artwork: ${response.statusCode}');
      }
    } on DioException catch (e) {
      throw Exception('Error updating artwork: ${e.message}');
    }
  }

  /// Delete an artwork
  Future<void> deleteArtwork(int artworkId) async {
    try {
      final response = await _httpClient.dio.delete('/api/artworks/$artworkId');

      if (response.statusCode != 204) {
        throw Exception('Failed to delete artwork: ${response.statusCode}');
      }
    } on DioException catch (e) {
      throw Exception('Error deleting artwork: ${e.message}');
    }
  }
}
