import 'package:flutter/material.dart';
import 'package:audioplayers/audioplayers.dart';
import '../../../core/constants/app_colors.dart';

/// WhatsApp-style audio message player widget
///
/// Features:
/// - Play/pause button
/// - Waveform visualization (simplified)
/// - Duration display
/// - Playback progress
class AudioMessageWidget extends StatefulWidget {
  final String audioUrl;
  final bool isUser;

  const AudioMessageWidget({
    super.key,
    required this.audioUrl,
    required this.isUser,
  });

  @override
  State<AudioMessageWidget> createState() => _AudioMessageWidgetState();
}

class _AudioMessageWidgetState extends State<AudioMessageWidget> {
  final AudioPlayer _audioPlayer = AudioPlayer();

  bool _isPlaying = false;
  Duration _duration = Duration.zero;
  Duration _position = Duration.zero;

  @override
  void initState() {
    super.initState();
    _initAudioPlayer();
  }

  void _initAudioPlayer() {
    // Listen to player state changes
    _audioPlayer.onPlayerStateChanged.listen((state) {
      if (mounted) {
        setState(() {
          _isPlaying = state == PlayerState.playing;
        });
      }
    });

    // Listen to duration changes
    _audioPlayer.onDurationChanged.listen((duration) {
      if (mounted) {
        setState(() {
          _duration = duration;
        });
      }
    });

    // Listen to position changes
    _audioPlayer.onPositionChanged.listen((position) {
      if (mounted) {
        setState(() {
          _position = position;
        });
      }
    });

    // Auto-reset when playback completes
    _audioPlayer.onPlayerComplete.listen((event) {
      if (mounted) {
        setState(() {
          _position = Duration.zero;
          _isPlaying = false;
        });
      }
    });
  }

  @override
  void dispose() {
    _audioPlayer.dispose();
    super.dispose();
  }

  Future<void> _togglePlayPause() async {
    if (_isPlaying) {
      await _audioPlayer.pause();
    } else {
      await _audioPlayer.play(UrlSource(widget.audioUrl));
    }
  }

  String _formatDuration(Duration duration) {
    String twoDigits(int n) => n.toString().padLeft(2, '0');
    final minutes = twoDigits(duration.inMinutes.remainder(60));
    final seconds = twoDigits(duration.inSeconds.remainder(60));
    return '$minutes:$seconds';
  }

  @override
  Widget build(BuildContext context) {
    final progress = _duration.inMilliseconds > 0
        ? _position.inMilliseconds / _duration.inMilliseconds
        : 0.0;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Play/Pause button
          Container(
            decoration: BoxDecoration(
              color: widget.isUser
                  ? Colors.white.withValues(alpha: 0.3)
                  : AppColors.primary.withValues(alpha: 0.1),
              shape: BoxShape.circle,
            ),
            child: IconButton(
              onPressed: _togglePlayPause,
              icon: Icon(
                _isPlaying ? Icons.pause : Icons.play_arrow,
                color: widget.isUser ? Colors.white : AppColors.primary,
              ),
              iconSize: 24,
              padding: const EdgeInsets.all(8),
              constraints: const BoxConstraints(),
            ),
          ),
          const SizedBox(width: 12),

          // Waveform and progress
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Simplified waveform
                SizedBox(
                  height: 32,
                  child: Stack(
                    children: [
                      // Background waveform
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        crossAxisAlignment: CrossAxisAlignment.center,
                        children: List.generate(40, (index) {
                          final heights = [12.0, 20.0, 16.0, 28.0, 14.0];
                          final height = heights[index % heights.length];
                          return Container(
                            width: 2,
                            height: height,
                            decoration: BoxDecoration(
                              color: widget.isUser
                                  ? Colors.white.withValues(alpha: 0.3)
                                  : AppColors.divider,
                              borderRadius: BorderRadius.circular(1),
                            ),
                          );
                        }),
                      ),
                      // Progress overlay
                      ClipRect(
                        child: Align(
                          alignment: Alignment.centerLeft,
                          widthFactor: progress,
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            crossAxisAlignment: CrossAxisAlignment.center,
                            children: List.generate(40, (index) {
                              final heights = [12.0, 20.0, 16.0, 28.0, 14.0];
                              final height = heights[index % heights.length];
                              return Container(
                                width: 2,
                                height: height,
                                decoration: BoxDecoration(
                                  color: widget.isUser
                                      ? Colors.white
                                      : AppColors.primary,
                                  borderRadius: BorderRadius.circular(1),
                                ),
                              );
                            }),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 4),
                // Duration
                Text(
                  _isPlaying || _position.inSeconds > 0
                      ? _formatDuration(_position)
                      : _formatDuration(_duration),
                  style: TextStyle(
                    fontSize: 12,
                    color: widget.isUser
                        ? Colors.white.withValues(alpha: 0.8)
                        : AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),

          // Microphone icon
          Icon(
            Icons.mic,
            size: 16,
            color: widget.isUser
                ? Colors.white.withValues(alpha: 0.6)
                : AppColors.textSecondary,
          ),
        ],
      ),
    );
  }
}
