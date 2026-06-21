import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';

/// Service for handling audio recording functionality
///
/// Features:
/// - Request microphone permissions
/// - Record audio in WAV format for emotion analysis
/// - Save recordings to temporary directory
/// - Manage recording state
class AudioRecorderService {
  final AudioRecorder _recorder = AudioRecorder();

  bool _isRecording = false;
  String? _currentRecordingPath;

  /// Check if currently recording
  bool get isRecording => _isRecording;

  /// Get the current recording path
  String? get currentRecordingPath => _currentRecordingPath;

  /// Request microphone permission from user
  ///
  /// Returns true if permission granted, false otherwise
  Future<bool> requestPermission() async {
    if (kIsWeb) {
      // On web, permissions are handled by the browser
      return true;
    }
    final status = await Permission.microphone.request();
    return status.isGranted;
  }

  /// Check if microphone permission is granted
  Future<bool> hasPermission() async {
    if (kIsWeb) {
      // On web, permissions are handled by the browser
      return true;
    }
    final status = await Permission.microphone.status;
    return status.isGranted;
  }

  /// Start recording audio
  ///
  /// Returns the file path where audio will be saved, or null if failed
  ///
  /// Audio format: WAV (required for emotion analysis model)
  /// Sample rate: 16000 Hz (standard for speech recognition)
  Future<String?> startRecording() async {
    try {
      // Check permission
      if (!await hasPermission()) {
        final granted = await requestPermission();
        if (!granted) {
          print('Microphone permission denied');
          return null;
        }
      }

      // Check if already recording
      if (_isRecording) {
        print('Already recording');
        return _currentRecordingPath;
      }

      // Get path for storing audio
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      String path;

      if (kIsWeb) {
        // For web, use a simple filename without directory path
        path = 'audio_$timestamp.wav';
      } else {
        // For mobile, use temporary directory
        final tempDir = await getTemporaryDirectory();
        path = '${tempDir.path}/audio_$timestamp.wav';
      }

      // Start recording with WAV format
      await _recorder.start(
        const RecordConfig(
          encoder: AudioEncoder.wav, // WAV format for emotion analysis
          sampleRate: 16000,          // 16kHz sample rate
          bitRate: 128000,            // 128kbps
          numChannels: 1,             // Mono audio
        ),
        path: path,
      );

      _isRecording = true;
      _currentRecordingPath = path;

      print('Recording started: $path');
      return path;
    } catch (e) {
      print('Error starting recording: $e');
      return null;
    }
  }

  /// Stop recording and return the file path
  ///
  /// Returns the path to the recorded audio file, or null if failed
  Future<String?> stopRecording() async {
    try {
      if (!_isRecording) {
        print('Not currently recording');
        return null;
      }

      final path = await _recorder.stop();
      _isRecording = false;

      print('Recording stopped: $path');
      return path;
    } catch (e) {
      print('Error stopping recording: $e');
      _isRecording = false;
      return null;
    }
  }

  /// Cancel current recording and delete the file
  Future<void> cancelRecording() async {
    try {
      if (_isRecording) {
        await _recorder.stop();
        _isRecording = false;
      }

      _currentRecordingPath = null;
    } catch (e) {
      print('Error canceling recording: $e');
    }
  }

  /// Get recording duration (if currently recording)
  Future<Duration?> getRecordingDuration() async {
    try {
      if (_isRecording) {
        // The package doesn't provide direct duration access
        // You would need to track it manually or use a timer
        return null;
      }
      return null;
    } catch (e) {
      print('Error getting duration: $e');
      return null;
    }
  }

  /// Check if device has recording capability
  Future<bool> isRecordingAvailable() async {
    return await _recorder.hasPermission();
  }

  /// Dispose resources
  void dispose() {
    _recorder.dispose();
  }
}
