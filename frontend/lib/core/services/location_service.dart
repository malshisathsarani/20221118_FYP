import 'package:geolocator/geolocator.dart';

class LocationService {
  /// Check if location services are enabled
  Future<bool> isLocationServiceEnabled() async {
    return await Geolocator.isLocationServiceEnabled();
  }

  /// Check location permission
  Future<LocationPermission> checkPermission() async {
    return await Geolocator.checkPermission();
  }

  /// Request location permission
  Future<LocationPermission> requestPermission() async {
    return await Geolocator.requestPermission();
  }

  /// Get current location
  /// Returns null if permission denied or location unavailable
  Future<Map<String, double>?> getCurrentLocation() async {
    try {
      // Check if location services are enabled
      bool serviceEnabled = await isLocationServiceEnabled();
      if (!serviceEnabled) {
        print('Location services are disabled');
        return null;
      }

      // Check permission
      LocationPermission permission = await checkPermission();

      if (permission == LocationPermission.denied) {
        permission = await requestPermission();
        if (permission == LocationPermission.denied) {
          print('Location permission denied');
          return null;
        }
      }

      if (permission == LocationPermission.deniedForever) {
        print('Location permissions are permanently denied');
        return null;
      }

      // Get current position
      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
        timeLimit: const Duration(seconds: 10),
      );

      return {
        'latitude': position.latitude,
        'longitude': position.longitude,
      };
    } catch (e) {
      print('Error getting location: $e');
      return null;
    }
  }

  /// Get current location with timeout
  /// Returns null if location not available within timeout
  Future<Map<String, double>?> getCurrentLocationWithTimeout({
    Duration timeout = const Duration(seconds: 5),
  }) async {
    try {
      final location = await getCurrentLocation().timeout(
        timeout,
        onTimeout: () {
          print('Location request timed out');
          return null;
        },
      );
      return location;
    } catch (e) {
      print('Error getting location: $e');
      return null;
    }
  }

  /// Open device location settings
  Future<bool> openLocationSettings() async {
    return await Geolocator.openLocationSettings();
  }
}
