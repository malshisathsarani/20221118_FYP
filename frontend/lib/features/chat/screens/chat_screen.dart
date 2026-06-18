import 'package:flutter/material.dart';
import '../../../shared/presentation/widgets/custom_app_bar.dart';
import '../../../shared/presentation/widgets/safety_banner.dart';
import '../../../core/services/chat_service.dart';
import '../../../core/models/chat_model.dart';
import '../../../core/constants/app_colors.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> with TickerProviderStateMixin {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final ChatService _chatService = ChatService();

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
      gradient: [Color(0xFFBBDEFB), Color(0xFFE3F2FD)],
      userBubble: Color(0xFF42A5F5),
      botBubble: Color(0xFFF1F8FF),
    ),
    ChatTheme(
      name: 'Gentle Green',
      gradient: [Color(0xFFC8E6C9), Color(0xFFE8F5E9)],
      userBubble: Color(0xFF66BB6A),
      botBubble: Color(0xFFF1F8F4),
    ),
    ChatTheme(
      name: 'Soft Purple',
      gradient: [Color(0xFFE1BEE7), Color(0xFFF3E5F5)],
      userBubble: Color(0xFFAB47BC),
      botBubble: Color(0xFFFAF4FB),
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
      final sessionId = await _chatService.createSession();
      setState(() {
        _sessionId = sessionId;
      });
      _addMessage(
        text: 'Hello! I\'m here to support you. How are you feeling today?',
        isUser: false,
      );
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
  }) {
    setState(() {
      _messages.add({
        'text': text,
        'isUser': isUser,
        'emotion': emotion,
        'crisis': crisis,
        'timestamp': DateTime.now(),
      });
    });
    _scrollToBottom();
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

  Future<void> _sendMessage() async {
    final text = _messageController.text.trim();
    if (text.isEmpty || _sessionId == null) return;

    _addMessage(text: text, isUser: true);
    _messageController.clear();
    setState(() => _isTyping = true);

    try {
      final chatMessage = await _chatService.sendMessage(
        sessionId: _sessionId!,
        message: text,
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
      );
    } catch (e) {
      setState(() => _isTyping = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to send message: $e')),
        );
      }
    }
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
                      transform: Matrix4.identity()..scale(scale),
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
          Expanded(
            child: TextField(
              controller: _messageController,
              style: const TextStyle(color: AppColors.textPrimary),
              decoration: InputDecoration(
                hintText: 'Type your message...',
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
          IconButton(
            onPressed: _sendMessage,
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
