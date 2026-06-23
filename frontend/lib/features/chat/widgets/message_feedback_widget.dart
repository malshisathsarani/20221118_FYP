import 'package:flutter/material.dart';

typedef FeedbackCallback = void Function(bool helpful, String? comment);

class MessageFeedbackWidget extends StatefulWidget {
  final int messageId;
  final FeedbackCallback onFeedback;
  final bool isVisible;

  const MessageFeedbackWidget({
    super.key,
    required this.messageId,
    required this.onFeedback,
    this.isVisible = true,
  });

  @override
  State<MessageFeedbackWidget> createState() => _MessageFeedbackWidgetState();
}

class _MessageFeedbackWidgetState extends State<MessageFeedbackWidget> {
  bool _isSubmitted = false;
  bool _showThanks = false;

  @override
  Widget build(BuildContext context) {
    if (!widget.isVisible) {
      return const SizedBox.shrink();
    }

    // Show thank you message
    if (_showThanks) {
      return Padding(
        padding: const EdgeInsets.only(top: 8),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.check_circle,
              size: 14,
              color: Colors.green.shade600,
            ),
            const SizedBox(width: 4),
            Text(
              'Thanks for your feedback!',
              style: TextStyle(
                fontSize: 11,
                color: Colors.green.shade700,
                fontStyle: FontStyle.italic,
              ),
            ),
          ],
        ),
      );
    }

    // Hide completely after submitted
    if (_isSubmitted) {
      return const SizedBox.shrink();
    }

    return Padding(
      padding: const EdgeInsets.only(top: 8),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            'Helpful?',
            style: TextStyle(
              fontSize: 11,
              color: Colors.grey.shade600,
            ),
          ),
          const SizedBox(width: 8),
          // Thumbs up
          InkWell(
            onTap: () => _handleFeedback(true),
            borderRadius: BorderRadius.circular(16),
            child: Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: Colors.grey.shade100,
                shape: BoxShape.circle,
              ),
              child: Icon(
                Icons.thumb_up_outlined,
                size: 16,
                color: Colors.grey.shade700,
              ),
            ),
          ),
          const SizedBox(width: 6),
          // Thumbs down
          InkWell(
            onTap: () => _handleFeedback(false),
            borderRadius: BorderRadius.circular(16),
            child: Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: Colors.grey.shade100,
                shape: BoxShape.circle,
              ),
              child: Icon(
                Icons.thumb_down_outlined,
                size: 16,
                color: Colors.grey.shade700,
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _handleFeedback(bool helpful) async {
    // Submit feedback
    widget.onFeedback(helpful, null);

    // Show thank you message
    if (mounted) {
      setState(() {
        _showThanks = true;
      });

      // Hide after 2 seconds
      await Future.delayed(const Duration(seconds: 2));

      if (mounted) {
        setState(() {
          _showThanks = false;
          _isSubmitted = true;
        });

        // Show again after 3 seconds
        await Future.delayed(const Duration(seconds: 3));

        if (mounted) {
          setState(() {
            _isSubmitted = false;
          });
        }
      }
    }
  }
}
