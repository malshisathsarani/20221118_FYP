import 'package:flutter/material.dart';
import '../../../core/services/feedback_service.dart';
import '../../../core/models/feedback_model.dart';

typedef FeedbackCallback = void Function(bool helpful, String? comment);

class MessageFeedbackWidget extends StatefulWidget {
  final int chatId;
  final FeedbackCallback? onFeedback;
  final bool isVisible;

  const MessageFeedbackWidget({
    super.key,
    required this.chatId,
    this.onFeedback,
    this.isVisible = true,
  });

  @override
  State<MessageFeedbackWidget> createState() => _MessageFeedbackWidgetState();
}

class _MessageFeedbackWidgetState extends State<MessageFeedbackWidget> {
  final FeedbackService _feedbackService = FeedbackService();
  bool? _selectedFeedback;
  bool _showCommentField = false;
  final TextEditingController _commentController = TextEditingController();
  bool _isSubmitting = false;
  bool _isSubmitted = false;
  String? _errorMessage;

  @override
  void dispose() {
    _commentController.dispose();
    super.dispose();
  }

  void _handleFeedback(bool helpful) {
    setState(() {
      _selectedFeedback = helpful;
      _showCommentField = !helpful; // Show comment field only if unhelpful
    });
  }

  void _submitFeedback() async {
    if (_selectedFeedback == null) return;

    setState(() {
      _isSubmitting = true;
      _errorMessage = null;
    });

    try {
      // Submit feedback to backend
      await _feedbackService.submitFeedback(
        chatId: widget.chatId,
        rating: _selectedFeedback! ? 5 : 1, // 5 for helpful, 1 for unhelpful
        feedbackType: FeedbackType.responseQuality,
        comment: _showCommentField ? _commentController.text.trim() : null,
      );

      // Call optional callback
      if (widget.onFeedback != null) {
        widget.onFeedback!(
          _selectedFeedback!,
          _showCommentField ? _commentController.text.trim() : null,
        );
      }

      if (mounted) {
        setState(() {
          _isSubmitting = false;
          _isSubmitted = true;
        });

        // Show success message
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✓ Thanks for your feedback!'),
            duration: Duration(seconds: 2),
            backgroundColor: Color(0xFF4CAF50),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
          _errorMessage = e.toString().replaceAll('Exception: ', '');
        });

        // Show error message
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to submit feedback: $_errorMessage'),
            duration: const Duration(seconds: 3),
            backgroundColor: Colors.red.shade600,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.isVisible) {
      return const SizedBox.shrink();
    }

    if (_isSubmitted) {
      return Padding(
        padding: const EdgeInsets.only(top: 8),
        child: Row(
          children: [
            Icon(Icons.check_circle_rounded, size: 14, color: Colors.green.shade600),
            const SizedBox(width: 6),
            Text(
              'Thanks for your feedback!',
              style: TextStyle(
                fontSize: 11,
                color: Colors.grey.shade600,
                fontStyle: FontStyle.italic,
              ),
            ),
          ],
        ),
      );
    }

    return Padding(
      padding: const EdgeInsets.only(top: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Feedback buttons with question
          Row(
            children: [
              Text(
                'Helpful?',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey.shade600,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(width: 10),

              // Yes button
              Material(
                color: Colors.transparent,
                child: InkWell(
                  onTap: _isSubmitting ? null : () => _handleFeedback(true),
                  borderRadius: BorderRadius.circular(20),
                  child: Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: _selectedFeedback == true
                          ? const Color(0xFF10B981)
                          : Colors.grey.shade100,
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      Icons.thumb_up_rounded,
                      size: 16,
                      color: _selectedFeedback == true
                          ? Colors.white
                          : Colors.grey.shade600,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 8),

              // No button
              Material(
                color: Colors.transparent,
                child: InkWell(
                  onTap: _isSubmitting ? null : () => _handleFeedback(false),
                  borderRadius: BorderRadius.circular(20),
                  child: Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: _selectedFeedback == false
                          ? const Color(0xFFEF4444)
                          : Colors.grey.shade100,
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      Icons.thumb_down_rounded,
                      size: 16,
                      color: _selectedFeedback == false
                          ? Colors.white
                          : Colors.grey.shade600,
                    ),
                  ),
                ),
              ),

              // Submit button inline (only show if feedback selected)
              if (_selectedFeedback != null) ...[
                const SizedBox(width: 12),
                Material(
                  color: Colors.transparent,
                  child: InkWell(
                    onTap: _isSubmitting ? null : _submitFeedback,
                    borderRadius: BorderRadius.circular(16),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(16),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.1),
                            blurRadius: 6,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child: _isSubmitting
                          ? SizedBox(
                              width: 10,
                              height: 10,
                              child: CircularProgressIndicator(
                                strokeWidth: 1.5,
                                valueColor: AlwaysStoppedAnimation<Color>(Colors.blue.shade600),
                              ),
                            )
                          : Text(
                              'Submit',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w600,
                                color: Colors.blue.shade600,
                              ),
                            ),
                    ),
                  ),
                ),
              ],
            ],
          ),

          // Comment field (only show if "No" selected)
          if (_showCommentField) ...[
            const SizedBox(height: 10),
            Container(
              decoration: BoxDecoration(
                color: Colors.grey.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: Colors.grey.shade300,
                  width: 1,
                ),
              ),
              child: TextField(
                controller: _commentController,
                style: const TextStyle(
                  fontSize: 12,
                  color: Colors.black87,
                ),
                decoration: InputDecoration(
                  hintText: 'What could be better?',
                  hintStyle: TextStyle(
                    fontSize: 12,
                    color: Colors.grey.shade400,
                  ),
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 8,
                  ),
                  border: InputBorder.none,
                  counterStyle: TextStyle(
                    fontSize: 10,
                    color: Colors.grey.shade500,
                  ),
                  isDense: true,
                ),
                maxLines: 2,
                maxLength: 200,
                onChanged: (value) {
                  setState(() {});
                },
              ),
            ),
          ],
        ],
      ),
    );
  }
}
