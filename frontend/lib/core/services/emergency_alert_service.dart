import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../utils/storage_helper.dart';
import '../models/emergency_contact.dart';

class EmergencyAlertService {
  final String baseUrl = ApiConfig.baseUrl;

  /// Send emergency alert to contact
  Future<Map<String, dynamic>> sendEmergencyAlert({
    required int contactId,
    required String riskLevel,
    required double riskScore,
    required String detectedEmotion,
    String crisisReason = "Crisis detected by AI system",
    double? latitude,
    double? longitude,
    bool sendSms = true,
    bool makeCall = false,
  }) async {
    try {
      final token = await StorageHelper.getAccessToken();

      if (token == null) {
        throw Exception('No access token found');
      }

      final response = await http.post(
        Uri.parse('$baseUrl/api/emergency-alert/send'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({
          'contact_id': contactId,
          'risk_level': riskLevel,
          'risk_score': riskScore,
          'detected_emotion': detectedEmotion,
          'crisis_reason': crisisReason,
          'latitude': latitude,
          'longitude': longitude,
          'send_sms': sendSms,
          'make_call': makeCall,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {
          'success': true,
          'data': data,
        };
      } else {
        final error = jsonDecode(response.body);
        return {
          'success': false,
          'error': error['detail'] ?? 'Failed to send emergency alert',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: ${e.toString()}',
      };
    }
  }

  /// Get emergency contacts
  Future<List<EmergencyContactModel>> getEmergencyContacts() async {
    try {
      final token = await StorageHelper.getAccessToken();

      if (token == null) {
        throw Exception('No access token found');
      }

      final response = await http.get(
        Uri.parse('$baseUrl/api/emergency-alert/contacts'),
        headers: {
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final contacts = (data['contacts'] as List)
            .map((contact) => EmergencyContactModel.fromJson(contact))
            .toList();
        return contacts;
      } else {
        throw Exception('Failed to fetch emergency contacts');
      }
    } catch (e) {
      throw Exception('Error fetching emergency contacts: ${e.toString()}');
    }
  }

  /// Test Twilio connection
  Future<Map<String, dynamic>> testTwilioConnection() async {
    try {
      final token = await StorageHelper.getAccessToken();

      if (token == null) {
        throw Exception('No access token found');
      }

      final response = await http.get(
        Uri.parse('$baseUrl/api/emergency-alert/test-twilio'),
        headers: {
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        final error = jsonDecode(response.body);
        return {
          'success': false,
          'error': error['detail'] ?? 'Twilio connection failed',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: ${e.toString()}',
      };
    }
  }
}
