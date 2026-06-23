import 'package:flutter/material.dart';
import '../../../shared/presentation/widgets/custom_app_bar.dart';
import '../../../shared/presentation/widgets/safety_banner.dart';
import '../../../core/services/chat_service.dart';
import '../../../core/services/emergency_alert_service.dart';
import '../../../core/services/feedback_service.dart';
import '../../../core/models/chat_model.dart';
import '../../../core/models/emergency_contact.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/utils/storage_helper.dart';
import '../widgets/audio_recorder_widget.dart';
import '../widgets/audio_message_widget.dart';
import '../widgets/message_feedback_widget.dart';
import '../dialogs/modern_crisis_dialog.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> with TickerProviderStateMixin {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final ChatService _chatService = ChatService();
  final FeedbackService _feedbackService = FeedbackService();

  final List<Map<String, dynamic>> _messages = [];
  String? _sessionId;
  bool _isTyping = false;
  bool _showCrisisWarning = false;

  // Animation controllers
  AnimationController? _floatingController;
  AnimationController? _typingController;

  // Color theme state
  int _currentThemeIndex = 0;
  final List<ChatTheme> _themes = [
    ChatTheme(
      name: 'Soft Blue',
      gradient: const [Color(0xFFBBDEFB), Color(0xFFE3F2FD)],
      userBubble: const Color(0xFF42A5F5),
      botBubble: const Color(0xFFF1F8FF),
    ),
    ChatTheme(
      name: 'Gentle Green',
      gradient: const [Color(0xFFC8E6C9), Color(0xFFE8F5E9)],
      userBubble: const Color(0xFF66BB6A),
      botBubble: const Color(0xFFF1F8F4),
    ),
    ChatTheme(
      name: 'Soft Purple',
      gradient: const [Color(0xFFE1BEE7), Color(0xFFF3E5F5)],
      userBubble: const Color(0xFFAB47BC),
      botBubble: const Color(0xFFFAF4FB),
    ),
  ];

  @override
  void initState() {
    super.initState();
    _floatingController = AnimationController(
      duration: const Duration(seconds: 4),
      vsync: this,
    )..repeat(reverse: true);

    _typingController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    )..repeat();

    _initializeChat();
  }

  Future<void> _initializeChat() async {
    try {
      // Try to load existing session ID
      final savedSessionId = await StorageHelper.getCurrentSessionId();

      if (savedSessionId != null) {
        // Resume existing session
        setState(() {
          _sessionId = savedSessionId;
        });

        // Load chat history from backend
        try {
          final history = await _chatService.getChatHistory(sessionId: savedSessionId);

          if (history.isNotEmpty) {
            // Load previous messages
            for (var chatMessage in history) {
              // Add user message
              _addMessage(
                text: chatMessage.message,
                isUser: true,
                skipScroll: true,
              );
              // Add bot response
              _addMessage(
                text: chatMessage.response,
                isUser: false,
                emotion: chatMessage.emotionAnalysis,
                crisis: chatMessage.crisisDetection,
                audioUrl: chatMessage.audioUrl,
                skipScroll: true,
              );
            }
            // Scroll to bottom after loading all messages
            Future.delayed(const Duration(milliseconds: 100), _scrollToBottom);
          } else {
            // No history, show welcome back message
            _addMessage(
              text: 'Welcome back! How are you feeling?',
              isUser: false,
            );
          }
        } catch (e) {
          // If loading history fails, just show welcome message
          // Error: $e
          _addMessage(
            text: 'Welcome back! How are you feeling?',
            isUser: false,
          );
        }
      } else {
        // Create new session
        final sessionId = await _chatService.createSession();
        setState(() {
          _sessionId = sessionId;
        });
        // Save session ID for persistence
        await StorageHelper.saveCurrentSessionId(sessionId);
        _addMessage(
          text: 'Hello! I\'m here to support you. How are you feeling today?',
          isUser: false,
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to start chat: $e')),
        );
      }
    }
  }

  void _addMessage({
    required String text,
    required bool isUser,
    EmotionAnalysis? emotion,
    CrisisDetection? crisis,
    String? audioUrl,
    int? messageId,
    bool skipScroll = false,
  }) {
    setState(() {
      _messages.add({
        'text': text,
        'isUser': isUser,
        'emotion': emotion,
        'crisis': crisis,
        'audioUrl': audioUrl,
        'messageId': messageId,
        'timestamp': DateTime.now(),
      });
    });
    if (!skipScroll) {
      _scrollToBottom();
    }
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _handleFeedback(int messageId, bool helpful, String? comment) async {
    try {
      // Convert helpful boolean to rating (5 for helpful, 2 for not helpful)
      final rating = helpful ? 5 : 2;

      await _feedbackService.submitFeedback(
        chatId: messageId,
        rating: rating,
        feedbackType: 'response_quality',
        comment: comment,
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to submit feedback: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _startNewChat() async {
    // Show confirmation dialog
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Start New Chat?'),
        content: const Text(
          'This will start a fresh conversation. Your current chat will be saved and you can access it later.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Start New'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      try {
        // Clear current session
        await StorageHelper.clearCurrentSession();

        // Clear messages
        setState(() {
          _messages.clear();
          _sessionId = null;
          _showCrisisWarning = false;
        });

        // Initialize new chat
        await _initializeChat();
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Failed to start new chat: $e')),
          );
        }
      }
    }
  }

  Future<void> _sendMessage({String? audioPath}) async {
    final text = _messageController.text.trim();
    if (text.isEmpty || _sessionId == null) return;

    _addMessage(text: text, isUser: true, audioUrl: audioPath);
    _messageController.clear();
    setState(() => _isTyping = true);

    try {
      final chatMessage = await _chatService.sendMessage(
        sessionId: _sessionId!,
        message: text,
        audioPath: audioPath, // Pass audio path for multi-modal analysis
      );

      setState(() {
        _isTyping = false;
        _showCrisisWarning = chatMessage.crisisDetection?.isCrisis ?? false;
      });

      _addMessage(
        text: chatMessage.response,
        isUser: false,
        emotion: chatMessage.emotionAnalysis,
        crisis: chatMessage.crisisDetection,
        audioUrl: chatMessage.audioUrl,
        messageId: chatMessage.id,
      );

      // Show emergency dialog for high/critical risk
      if (chatMessage.crisisDetection?.isCrisis == true) {
        _showEmergencyDialog(chatMessage.crisisDetection!, chatMessage.emotionAnalysis);
      }
    } catch (e) {
      setState(() => _isTyping = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to send message: $e')),
        );
      }
    }
  }

  /// Handle audio recording completion
  Future<void> _handleAudioRecorded(String audioPath) async {
    // If there's text in the message field, send both text and audio
    if (_messageController.text.trim().isNotEmpty) {
      await _sendMessage(audioPath: audioPath);
    } else {
      // Audio-only message
      _addMessage(text: '🎤 Voice message', isUser: true, audioUrl: audioPath);
      setState(() => _isTyping = true);

      try {
        final chatMessage = await _chatService.sendMessage(
          sessionId: _sessionId!,
          message: 'Voice message', // Placeholder text
          audioPath: audioPath,
        );

        setState(() {
          _isTyping = false;
          _showCrisisWarning = chatMessage.crisisDetection?.isCrisis ?? false;
        });

        _addMessage(
          text: chatMessage.response,
          isUser: false,
          emotion: chatMessage.emotionAnalysis,
          crisis: chatMessage.crisisDetection,
          audioUrl: chatMessage.audioUrl,
          messageId: chatMessage.id,
        );

        // Show emergency dialog for high/critical risk
        if (chatMessage.crisisDetection?.isCrisis == true) {
          _showEmergencyDialog(chatMessage.crisisDetection!, chatMessage.emotionAnalysis);
        }
      } catch (e) {
        setState(() => _isTyping = false);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Failed to send audio: $e')),
          );
        }
      }
    }
  }

  /// Show emergency confirmation dialog
  Future<void> _showEmergencyDialog(CrisisDetection crisis, EmotionAnalysis? emotionAnalysis) async {
    try {
      // Get emergency contacts
      final emergencyService = EmergencyAlertService();
      final contacts = await emergencyService.getEmergencyContacts();

      if (!mounted) return;

      // Location disabled for privacy - emergency contacts will be notified without GPS coordinates
      // final locationService = LocationService();
      // final location = await locationService.getCurrentLocationWithTimeout();

      if (!mounted) return;

      // Show modern emergency dialog with glassmorphism
      final dialogResult = await showDialog<Map<String, dynamic>>(
        context: context,
        barrierDismissible: false, // Cannot dismiss by tapping outside
        barrierColor: Colors.black.withValues(alpha: 0.7), // Darker backdrop for modern look
        builder: (context) => ModernCrisisDialog(
          riskScore: crisis.crisisScore,
          crisisReason: crisis.indicators?.join(', ') ?? 'Crisis indicators detected',
          contacts: contacts,
          countdownSeconds: 30,
          onConfirm: (EmergencyContactModel contact) async {
            // Send emergency alert
            try {
              final result = await emergencyService.sendEmergencyAlert(
                contactId: contact.id!,
                riskLevel: _getRiskLevel(crisis.crisisScore),
                riskScore: crisis.crisisScore,
                detectedEmotion: emotionAnalysis?.emotion ?? 'distressed',
                crisisReason: crisis.indicators?.join(', ') ?? 'Crisis indicators detected',
                latitude: null, // Location disabled for privacy
                longitude: null, // Location disabled for privacy
                sendSms: true,
                makeCall: crisis.crisisScore >= 0.85, // Call for critical only
              );

              // Return result to be shown after dialog is closed
              // Use a safer approach by checking if context is still mounted
              if (context.mounted) {
                Navigator.of(context).pop({
                  'success': result['success'],
                  'error': result['error'],
                  'contactName': contact.name,
                });
              }
            } catch (e) {
              // Return error to be shown after dialog is closed
              if (context.mounted) {
                Navigator.of(context).pop({
                  'success': false,
                  'error': e.toString(),
                  'contactName': contact.name,
                });
              }
            }
          },
          onCancel: () {
            Navigator.of(context).pop({'cancelled': true});
          },
        ),
      );

      // Show result after dialog is closed
      if (!mounted) return;

      if (dialogResult != null) {
        if (dialogResult['cancelled'] == true) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Emergency alert cancelled'),
              duration: Duration(seconds: 2),
            ),
          );
        } else if (dialogResult['success'] == true) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Emergency alert sent to ${dialogResult['contactName']}'),
              backgroundColor: Colors.green,
            ),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Failed to send alert: ${dialogResult['error'] ?? 'Unknown error'}'),
              backgroundColor: Colors.red,
              duration: const Duration(seconds: 5),
            ),
          );
        }
      }
    } catch (e) {
      // Error showing emergency dialog: $e
      // Optionally show a fallback message
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('Unable to load emergency contacts. Please add contacts in settings.'),
            backgroundColor: Colors.orange,
            duration: const Duration(seconds: 4),
            action: SnackBarAction(
              label: 'Settings',
              textColor: Colors.white,
              onPressed: () {
                // Navigate to settings (you can implement this)
              },
            ),
          ),
        );
      }
    }
  }

  String _getRiskLevel(double crisisScore) {
    if (crisisScore >= 0.85) return 'critical';
    if (crisisScore >= 0.70) return 'high';
    if (crisisScore >= 0.45) return 'moderate';
    return 'low';
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    _floatingController?.dispose();
    _typingController?.dispose();
    super.dispose();
  }

  void _showThemeSelector() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        padding: const EdgeInsets.all(24),
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Choose Theme',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w700,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: List.generate(_themes.length, (index) {
                final theme = _themes[index];
                final isSelected = index == _currentThemeIndex;

                return GestureDetector(
                  onTap: () {
                    setState(() => _currentThemeIndex = index);
                    Navigator.pop(context);
                  },
                  child: Column(
                    children: [
                      Container(
                        width: 60,
                        height: 60,
                        decoration: BoxDecoration(
                          color: theme.userBubble,
                          shape: BoxShape.circle,
                          border: isSelected
                            ? Border.all(color: theme.userBubble, width: 4)
                            : null,
                          boxShadow: [
                            BoxShadow(
                              color: theme.userBubble.withValues(alpha: 0.4),
                              blurRadius: isSelected ? 12 : 6,
                              offset: const Offset(0, 2),
                            ),
                          ],
                        ),
                        child: isSelected
                          ? const Icon(Icons.check, color: Colors.white, size: 28)
                          : null,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        theme.name,
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                          color: isSelected ? AppColors.textPrimary : AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                );
              }),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final currentTheme = _themes[_currentThemeIndex];

    return Scaffold(
      appBar: CustomAppBar(
        title: 'Chat',
        subtitle: 'AI Mental Health Support',
        actions: [
          IconButton(
            icon: const Icon(Icons.add_comment_outlined, color: Colors.white),
            onPressed: _startNewChat,
            tooltip: 'New Chat',
          ),
          IconButton(
            icon: const Icon(Icons.palette_outlined, color: Colors.white),
            onPressed: _showThemeSelector,
            tooltip: 'Change Theme',
          ),
        ],
      ),
      body: Column(
        children: [
          if (_showCrisisWarning)
            SafetyBanner(
              onGetHelp: () => Navigator.pushNamed(context, '/crisis'),
            ),
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    currentTheme.gradient[0].withValues(alpha: 0.3),
                    Colors.white,
                  ],
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                ),
              ),
              child: Stack(
                children: [
                  // Animated floating bubbles
                  if (_floatingController != null)
                    AnimatedBuilder(
                      animation: _floatingController!,
                      builder: (context, child) {
                        return Stack(
                          children: [
                            _buildFloatingBubble(
                              top: 50 + (_floatingController!.value * 30),
                              left: 30,
                              size: 60,
                              color: currentTheme.gradient[0].withValues(alpha: 0.1),
                            ),
                            _buildFloatingBubble(
                              top: 150 + (_floatingController!.value * -20),
                              right: 40,
                              size: 80,
                              color: currentTheme.gradient[1].withValues(alpha: 0.08),
                            ),
                            _buildFloatingBubble(
                              bottom: 100 + (_floatingController!.value * 25),
                              left: 50,
                              size: 100,
                              color: currentTheme.gradient[0].withValues(alpha: 0.06),
                            ),
                            _buildFloatingBubble(
                              top: 300 + (_floatingController!.value * -15),
                              right: 60,
                              size: 70,
                              color: currentTheme.gradient[1].withValues(alpha: 0.09),
                            ),
                          ],
                        );
                      },
                    ),
                  // Messages
                  ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(16),
                    itemCount: _messages.length + (_isTyping ? 1 : 0),
                    itemBuilder: (context, index) {
                      if (_isTyping && index == _messages.length) {
                        return _buildTypingIndicator();
                      }
                      final message = _messages[index];
                      return _buildMessageBubble(message, index);
                    },
                  ),
                ],
              ),
            ),
          ),
          _buildInputArea(),
        ],
      ),
    );
  }

  Widget _buildFloatingBubble({
    double? top,
    double? bottom,
    double? left,
    double? right,
    required double size,
    required Color color,
  }) {
    return Positioned(
      top: top,
      bottom: bottom,
      left: left,
      right: right,
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: color,
        ),
      ),
    );
  }

  Widget _buildMessageBubble(Map<String, dynamic> message, int index) {
    final isUser = message['isUser'] as bool;
    final text = message['text'] as String;
    final emotion = message['emotion'] as EmotionAnalysis?;
    final crisis = message['crisis'] as CrisisDetection?;
    final audioUrl = message['audioUrl'] as String?;
    final messageId = message['messageId'] as int?;
    final currentTheme = _themes[_currentThemeIndex];

    return TweenAnimationBuilder<double>(
      duration: const Duration(milliseconds: 400),
      curve: Curves.easeOut,
      tween: Tween(begin: 0.0, end: 1.0),
      builder: (context, value, child) {
        return Opacity(
          opacity: value,
          child: Transform.translate(
            offset: Offset(0, 20 * (1 - value)),
            child: child,
          ),
        );
      },
      child: Align(
        alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
        child: Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(16),
          constraints: BoxConstraints(
            maxWidth: MediaQuery.of(context).size.width * 0.75,
          ),
          decoration: BoxDecoration(
            color: isUser ? currentTheme.userBubble : currentTheme.botBubble,
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              BoxShadow(
                color: isUser
                  ? currentTheme.userBubble.withValues(alpha: 0.3)
                  : Colors.black.withValues(alpha: 0.05),
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Audio player if audio URL exists
              if (audioUrl != null && audioUrl.isNotEmpty) ...[
                AudioMessageWidget(
                  audioUrl: audioUrl,
                  isUser: isUser,
                ),
                const SizedBox(height: 8),
              ],
              // Text message
              Text(
                text,
                style: TextStyle(
                  color: isUser ? Colors.white : AppColors.textPrimary,
                  fontSize: 15,
                  height: 1.4,
                ),
              ),
            if (emotion != null) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: isUser
                      ? Colors.white.withValues(alpha:0.2)
                      : AppColors.divider,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  '${emotion.emotion} (${(emotion.confidence * 100).toStringAsFixed(0)}%)',
                  style: TextStyle(
                    fontSize: 12,
                    color: isUser ? Colors.white : AppColors.textSecondary,
                  ),
                ),
              ),
            ],
            if (crisis != null && crisis.isCrisis) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: AppColors.error.withValues(alpha:0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.warning, size: 14, color: AppColors.error),
                    const SizedBox(width: 4),
                    Text(
                      'Crisis: ${crisis.severity ?? "detected"}',
                      style: const TextStyle(
                        fontSize: 12,
                        color: AppColors.error,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ],
            // Feedback widget for bot messages
            if (!isUser && messageId != null) ...[
              const SizedBox(height: 12),
              MessageFeedbackWidget(
                messageId: messageId,
                onFeedback: (helpful, comment) => _handleFeedback(
                  messageId,
                  helpful,
                  comment,
                ),
              ),
            ],
          ],
        ),
      ),
      ),
    );
  }

  Widget _buildTypingIndicator() {
    final currentTheme = _themes[_currentThemeIndex];

    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: currentTheme.botBubble,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.05),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (_typingController != null)
              ...List.generate(3, (index) {
                return AnimatedBuilder(
                  animation: _typingController!,
                  builder: (context, child) {
                    final delay = index * 0.2;
                    final animValue = (_typingController!.value + delay) % 1.0;
                    final scale = 0.5 + (animValue < 0.5
                      ? animValue
                      : 1.0 - animValue);

                    return Container(
                      margin: const EdgeInsets.symmetric(horizontal: 3),
                      width: 8,
                      height: 8,
                      transform: Matrix4.diagonal3Values(scale, scale, 1.0),
                      decoration: BoxDecoration(
                        color: currentTheme.userBubble.withValues(alpha: 0.6),
                        shape: BoxShape.circle,
                      ),
                    );
                  },
                );
              })
            else
              ...List.generate(3, (index) {
                return Container(
                  margin: const EdgeInsets.symmetric(horizontal: 3),
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: currentTheme.userBubble.withValues(alpha: 0.6),
                    shape: BoxShape.circle,
                  ),
                );
              }),
          ],
        ),
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha:0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Row(
        children: [
          // Audio recorder widget
          AudioRecorderWidget(
            onAudioRecorded: _handleAudioRecorded,
          ),
          const SizedBox(width: 8),

          // Text input
          Expanded(
            child: TextField(
              controller: _messageController,
              style: const TextStyle(color: AppColors.textPrimary),
              decoration: InputDecoration(
                hintText: 'Type or speak your message...',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                  borderSide: BorderSide.none,
                ),
                filled: true,
                fillColor: AppColors.surface,
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 20,
                  vertical: 12,
                ),
              ),
              onSubmitted: (_) => _sendMessage(),
            ),
          ),
          const SizedBox(width: 8),

          // Send button
          IconButton(
            onPressed: () => _sendMessage(),
            icon: const Icon(Icons.send),
            color: Theme.of(context).primaryColor,
            iconSize: 28,
          ),
        ],
      ),
    );
  }
}

class ChatTheme {
  final String name;
  final List<Color> gradient;
  final Color userBubble;
  final Color botBubble;

  ChatTheme({
    required this.name,
    required this.gradient,
    required this.userBubble,
    required this.botBubble,
  });
}
