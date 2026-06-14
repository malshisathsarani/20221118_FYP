import 'package:dio/dio.dart';
import '../network/http_client.dart';
import '../config/api_config.dart';
import '../models/emergency_contact.dart';

class EmergencyContactService {
  final HttpClient _httpClient = HttpClient();

  /// Get all emergency contacts for the current user
  Future<List<EmergencyContactModel>> getContacts() async {
    try {
      final response = await _httpClient.dio.get('/api/emergency-contacts/');

      if (response.statusCode == 200) {
        final List contactsJson = response.data['contacts'] as List;
        return contactsJson
            .map((json) => EmergencyContactModel.fromJson(json))
            .toList();
      } else {
        throw Exception('Failed to load contacts: ${response.statusCode}');
      }
    } on DioException catch (e) {
      throw Exception('Error loading contacts: ${e.message}');
    }
  }

  /// Create a new emergency contact
  Future<EmergencyContactModel> createContact(
      EmergencyContactModel contact) async {
    try {
      final response = await _httpClient.dio.post(
        '/api/emergency-contacts/',
        data: contact.toJson(),
      );

      if (response.statusCode == 201) {
        return EmergencyContactModel.fromJson(response.data);
      } else {
        throw Exception('Failed to create contact: ${response.statusCode}');
      }
    } on DioException catch (e) {
      throw Exception('Error creating contact: ${e.message}');
    }
  }

  /// Update an existing emergency contact
  Future<EmergencyContactModel> updateContact(
      int contactId, EmergencyContactModel contact) async {
    try {
      final response = await _httpClient.dio.put(
        '/api/emergency-contacts/$contactId',
        data: contact.toJson(),
      );

      if (response.statusCode == 200) {
        return EmergencyContactModel.fromJson(response.data);
      } else {
        throw Exception('Failed to update contact: ${response.statusCode}');
      }
    } on DioException catch (e) {
      throw Exception('Error updating contact: ${e.message}');
    }
  }

  /// Delete an emergency contact
  Future<void> deleteContact(int contactId) async {
    try {
      final response = await _httpClient.dio.delete(
        '/api/emergency-contacts/$contactId',
      );

      if (response.statusCode != 204) {
        throw Exception('Failed to delete contact: ${response.statusCode}');
      }
    } on DioException catch (e) {
      throw Exception('Error deleting contact: ${e.message}');
    }
  }

  /// Set a contact as primary
  Future<EmergencyContactModel> setPrimaryContact(int contactId) async {
    try {
      final response = await _httpClient.dio.patch(
        '/api/emergency-contacts/$contactId/set-primary',
      );

      if (response.statusCode == 200) {
        return EmergencyContactModel.fromJson(response.data);
      } else {
        throw Exception(
            'Failed to set primary contact: ${response.statusCode}');
      }
    } on DioException catch (e) {
      throw Exception('Error setting primary contact: ${e.message}');
    }
  }
}
