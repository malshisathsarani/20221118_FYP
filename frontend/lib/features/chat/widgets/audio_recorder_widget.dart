import 'package:flutter/material.dart';
import 'dart:async';
import '../../../core/services/audio_recorder_service.dart';
import '../../../core/constants/app_colors.dart';

/// Widget for recording audio messages with visual feedback
///
/// Features:
/// - Animated recording button with pulsing effect
/// - Duration timer during recording
/// - Cancel and send actions
/// - Permission handling
class AudioRecorderWidget extends StatefulWidget {
  /// Callback when audio recording is completed
  final Function(String audioPath) onAudioRecorded;

  /// Callback when recording is cancelled
  final VoidCallback? onCancel;

  const AudioRecorderWidget({
    super.key,
    required this.onAudioRecorded,
    this.onCancel,
  });

  @override
  State<AudioRecorderWidget> createState() => _AudioRecorderWidgetState();
}

class _AudioRecorderWidgetState extends State<AudioRecorderWidget>
    with SingleTickerProviderStateMixin {
  final AudioRecorderService _recorderService = AudioRecorderService();

  bool _isRecording = false;
  Duration _recordingDuration = Duration.zero;
  Timer? _durationTimer;
  AnimationController? _pulseController;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _durationTimer?.cancel();
    _pulseController?.dispose();
    _recorderService.dispose();
    super.dispose();
  }

  /// Start recording audio
  Future<void> _startRecording() async {
    final path = await _recorderService.startRecording();

    if (path != null) {
      setState(() {
        _isRecording = true;
        _recordingDuration = Duration.zero;
      });

      // Start duration timer
      _durationTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
        setState(() {
          _recordingDuration = Duration(seconds: timer.tick);
        });
      });
    } else {
      // Permission denied or error
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Microphone permission required to record audio'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    }
  }

  /// Stop recording and return the file
  Future<void> _stopRecording() async {
    _durationTimer?.cancel();

    final path = await _recorderService.stopRecording();

    if (path != null && mounted) {
      widget.onAudioRecorded(path);
      setState(() {
        _isRecording = false;
        _recordingDuration = Duration.zero;
      });
    }
  }

  /// Cancel recording and delete file
  Future<void> _cancelRecording() async {
    _durationTimer?.cancel();
    await _recorderService.cancelRecording();

    setState(() {
      _isRecording = false;
      _recordingDuration = Duration.zero;
    });

    widget.onCancel?.call();
  }

  /// Format duration to MM:SS
  String _formatDuration(Duration duration) {
    String twoDigits(int n) => n.toString().padLeft(2, '0');
    final minutes = twoDigits(duration.inMinutes.remainder(60));
    final seconds = twoDigits(duration.inSeconds.remainder(60));
    return '$minutes:$seconds';
  }

  @override
  Widget build(BuildContext context) {
    if (!_isRecording) {
      // Microphone button to start recording
      return IconButton(
        onPressed: _startRecording,
        icon: const Icon(Icons.mic_outlined),
        color: AppColors.textSecondary,
        iconSize: 28,
        tooltip: 'Record voice message',
      );
    }

    // Recording interface
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: AppColors.error.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(24),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Cancel button
          IconButton(
            onPressed: _cancelRecording,
            icon: const Icon(Icons.close),
            color: AppColors.error,
            iconSize: 24,
            tooltip: 'Cancel',
          ),
          const SizedBox(width: 8),

          // Pulsing recording indicator
          AnimatedBuilder(
            animation: _pulseController!,
            builder: (context, child) {
              return Container(
                width: 12,
                height: 12,
                decoration: BoxDecoration(
                  color: AppColors.error,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: AppColors.error.withValues(alpha: 0.6),
                      blurRadius: 8 * _pulseController!.value,
                      spreadRadius: 4 * _pulseController!.value,
                    ),
                  ],
                ),
              );
            },
          ),
          const SizedBox(width: 12),

          // Duration display
          Text(
            _formatDuration(_recordingDuration),
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: AppColors.error,
            ),
          ),
          const SizedBox(width: 16),

          // Send button
          Container(
            decoration: BoxDecoration(
              color: AppColors.primary,
              shape: BoxShape.circle,
            ),
            child: IconButton(
              onPressed: _stopRecording,
              icon: const Icon(Icons.send),
              color: Colors.white,
              iconSize: 20,
              tooltip: 'Send',
            ),
          ),
        ],
      ),
    );
  }
}
