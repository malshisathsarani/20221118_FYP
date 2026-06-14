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
  bool? _selectedFeedback;
  bool _showCommentField = false;
  final TextEditingController _commentController = TextEditingController();
  bool _isSubmitting = false;
  bool _isSubmitted = false;

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
    });

    // Call the feedback callback
    widget.onFeedback(
      _selectedFeedback!,
      _showCommentField ? _commentController.text.trim() : null,
    );

    // Show confirmation
    await Future.delayed(const Duration(milliseconds: 500));

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

      // Reset after 2 seconds
      Future.delayed(const Duration(seconds: 3), () {
        if (mounted) {
          setState(() {
            _selectedFeedback = null;
            _showCommentField = false;
            _commentController.clear();
            _isSubmitted = false;
          });
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.isVisible) {
      return const SizedBox.shrink();
    }

    if (_isSubmitted) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Text(
          '✓ Feedback received',
          style: TextStyle(
            fontSize: 12,
            color: Colors.green.shade600,
            fontStyle: FontStyle.italic,
          ),
        ),
      );
    }

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Feedback question
          Text(
            'Was this response helpful?',
            style: Theme.of(context).textTheme.labelSmall?.copyWith(
                  fontWeight: FontWeight.w500,
                  color: Colors.grey.shade700,
                ),
          ),
          const SizedBox(height: 8),

          // Feedback buttons
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Yes button
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: _isSubmitting ? null : () => _handleFeedback(true),
                  icon: const Icon(Icons.thumb_up_outlined, size: 16),
                  label: const Text('Yes', style: TextStyle(fontSize: 12)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _selectedFeedback == true
                        ? Colors.green.shade500
                        : Colors.grey.shade300,
                    foregroundColor: _selectedFeedback == true
                        ? Colors.white
                        : Colors.grey.shade700,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 8,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(6),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 8),

              // No button
              Expanded(
                child: ElevatedButton.icon(
                  onPressed:
                      _isSubmitting ? null : () => _handleFeedback(false),
                  icon: const Icon(Icons.thumb_down_outlined, size: 16),
                  label: const Text('No', style: TextStyle(fontSize: 12)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _selectedFeedback == false
                        ? Colors.red.shade500
                        : Colors.grey.shade300,
                    foregroundColor: _selectedFeedback == false
                        ? Colors.white
                        : Colors.grey.shade700,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 8,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(6),
                    ),
                  ),
                ),
              ),
            ],
          ),

          // Comment field (only show if "No" selected)
          if (_showCommentField) ...[
            const SizedBox(height: 8),
            TextField(
              controller: _commentController,
              decoration: InputDecoration(
                hintText: 'Tell us what could be better...',
                hintStyle: TextStyle(fontSize: 12, color: Colors.grey.shade400),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 8,
                ),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(6),
                  borderSide: BorderSide(color: Colors.grey.shade300),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(6),
                  borderSide: const BorderSide(
                    color: Color(0xFF1A695C),
                    width: 2,
                  ),
                ),
                suffixIcon: _commentController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear, size: 16),
                        onPressed: () {
                          setState(() {
                            _commentController.clear();
                          });
                        },
                      )
                    : null,
              ),
              maxLines: 2,
              minLines: 1,
              maxLength: 200,
              onChanged: (value) {
                setState(() {}); // Rebuild to update suffix icon
              },
            ),
          ],

          // Submit button (only show if feedback selected)
          if (_selectedFeedback != null) ...[
            const SizedBox(height: 8),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isSubmitting ? null : _submitFeedback,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF1A695C),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 8,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(6),
                  ),
                ),
                child: _isSubmitting
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor:
                              AlwaysStoppedAnimation<Color>(Colors.white),
                        ),
                      )
                    : const Text(
                        'Submit',
                        style: TextStyle(fontSize: 12),
                      ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
