import 'package:flutter/material.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/models/game_tracking_model.dart';
import '../../../core/services/game_tracking_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with TickerProviderStateMixin {
  late List<AnimationController> _controllers;
  late List<Animation<double>> _animations;
  final GameTrackingService _gameTrackingService = GameTrackingService();

  ProgressSummary? _progressSummary;
  WeeklyActivity? _weeklyActivity;
  bool _isLoadingProgress = true;

  @override
  void initState() {
    super.initState();

    // Create multiple floating bubble animations
    _controllers = List.generate(
      6,
      (index) => AnimationController(
        duration: Duration(seconds: 3 + index),
        vsync: this,
      )..repeat(reverse: true),
    );

    _animations = _controllers.map((controller) {
      return Tween<double>(begin: -20, end: 20).animate(
        CurvedAnimation(parent: controller, curve: Curves.easeInOut),
      );
    }).toList();

    _loadProgressData();
  }

  Future<void> _loadProgressData() async {
    try {
      final progress = await _gameTrackingService.getProgressSummary();
      final weekly = await _gameTrackingService.getWeeklyActivity();

      setState(() {
        _progressSummary = progress;
        _weeklyActivity = weekly;
        _isLoadingProgress = false;
      });
    } catch (e) {
      setState(() {
        _isLoadingProgress = false;
      });
      // Silently fail - progress is optional
    }
  }

  @override
  void dispose() {
    for (var controller in _controllers) {
      controller.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // Overlay gradient for better readability
          Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  AppColors.background.withValues(alpha: 0.7),
                  AppColors.background.withValues(alpha: 0.9),
                ],
              ),
            ),
          ),
          // Floating circles (optional - can be removed if too busy)
          Container(
            child: Stack(
              children: [
                _buildFloatingCircle(0, top: 50, left: 30, size: 80),
                _buildFloatingCircle(1, top: 150, right: 40, size: 60),
                _buildFloatingCircle(2, bottom: 200, left: 50, size: 100),
                _buildFloatingCircle(3, top: 300, right: 60, size: 70),
                _buildFloatingCircle(4, bottom: 100, right: 80, size: 90),
                _buildFloatingCircle(5, top: 450, left: 20, size: 50),
              ],
            ),
          ),
          // Content
          SafeArea(
            child: SingleChildScrollView(
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Header
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Welcome Back!',
                              style: TextStyle(
                                fontSize: 32,
                                fontWeight: FontWeight.w800,
                                color: AppColors.textPrimary,
                                letterSpacing: -1,
                              ),
                            ),
                            SizedBox(height: 4),
                            Text(
                              'How are you feeling today?',
                              style: TextStyle(
                                fontSize: 16,
                                color: AppColors.textSecondary,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ],
                        ),
                        Container(
                          decoration: BoxDecoration(
                            color: AppColors.primary,
                            shape: BoxShape.circle,
                            boxShadow: [
                              BoxShadow(
                                color: AppColors.primary.withValues(alpha:0.3),
                                blurRadius: 15,
                                spreadRadius: 2,
                              ),
                            ],
                          ),
                          child: IconButton(
                            icon: const Icon(Icons.person, color: Colors.white, size: 28),
                            onPressed: () => Navigator.pushNamed(context, '/profile'),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),

                    // Featured Card - Meet Assistant
                    _buildFeaturedCard(
                      context,
                      'Meet Assistant',
                      'Start a conversation with your AI wellness companion',
                      Icons.chat_bubble_rounded,
                      AppColors.primary,
                      () => Navigator.pushNamed(context, '/chat'),
                    ),
                    const SizedBox(height: 16),

                    // Other Features Grid
                    SizedBox(
                      height: 200,
                      child: Row(
                        children: [
                          Expanded(
                            child: _buildFeatureCard(
                              context,
                              'Crisis Resources',
                              'Get immediate help',
                              Icons.emergency,
                              AppColors.error,
                              () => Navigator.pushNamed(context, '/crisis'),
                            ),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: _buildFeatureCard(
                              context,
                              'Relaxation Tools',
                              'Breathing exercises',
                              Icons.spa,
                              AppColors.secondary,
                              () => Navigator.pushNamed(context, '/tools'),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Progress Summary Card - at bottom
                    if (!_isLoadingProgress && _progressSummary != null)
                      _buildProgressCard(),
                    const SizedBox(height: 20),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFloatingCircle(
    int index, {
    double? top,
    double? bottom,
    double? left,
    double? right,
    required double size,
  }) {
    final colors = [
      AppColors.primary.withValues(alpha:0.08),
      AppColors.secondary.withValues(alpha:0.08),
      AppColors.accent.withValues(alpha:0.08),
    ];

    return AnimatedBuilder(
      animation: _animations[index],
      builder: (context, child) {
        return Positioned(
          top: top != null ? top + _animations[index].value : null,
          bottom: bottom != null ? bottom + _animations[index].value : null,
          left: left,
          right: right,
          child: Container(
            width: size,
            height: size,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: colors[index % colors.length],
              boxShadow: [
                BoxShadow(
                  color: colors[index % colors.length].withValues(alpha:0.3),
                  blurRadius: 20,
                  spreadRadius: 5,
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildFeaturedCard(
    BuildContext context,
    String title,
    String subtitle,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              color,
              color.withValues(alpha:0.8),
            ],
          ),
          borderRadius: BorderRadius.circular(24),
          boxShadow: [
            BoxShadow(
              color: color.withValues(alpha:0.3),
              blurRadius: 20,
              spreadRadius: 2,
              offset: const Offset(0, 8),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha:0.2),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Icon(icon, size: 48, color: Colors.white),
            ),
            const SizedBox(width: 20),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.w800,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    subtitle,
                    style: TextStyle(
                      fontSize: 15,
                      color: Colors.white.withValues(alpha:0.9),
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
            const Icon(
              Icons.arrow_forward_ios,
              color: Colors.white,
              size: 24,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFeatureCard(
    BuildContext context,
    String title,
    String subtitle,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(
            color: AppColors.divider,
            width: 1,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha:0.05),
              blurRadius: 10,
              spreadRadius: 0,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: color.withValues(alpha:0.1),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Icon(icon, size: 40, color: color),
            ),
            const SizedBox(height: 16),
            Text(
              title,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w700,
                color: AppColors.textPrimary,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 6),
            Text(
              subtitle,
              style: const TextStyle(
                fontSize: 13,
                color: AppColors.textSecondary,
                fontWeight: FontWeight.w500,
              ),
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProgressCard() {
    final progress = _progressSummary!;
    final weekly = _weeklyActivity;

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppColors.divider, width: 1),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.08),
            blurRadius: 20,
            spreadRadius: 0,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with streak
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFFFF6B6B), Color(0xFFFF8E53)],
                  ),
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFFFF6B6B).withValues(alpha: 0.3),
                      blurRadius: 8,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: const Icon(
                  Icons.local_fire_department,
                  color: Colors.white,
                  size: 28,
                ),
              ),
              const SizedBox(width: 12),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '${progress.currentStreakDays} Day Streak',
                    style: const TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.w800,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const Text(
                    'Keep it going! 🎉',
                    style: TextStyle(
                      fontSize: 14,
                      color: AppColors.textSecondary,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 24),

          // Stats Grid with gradient cards
          Row(
            children: [
              Expanded(
                child: _buildGradientStatCard(
                  Icons.sports_esports,
                  progress.totalSessions.toString(),
                  'Sessions',
                  [const Color(0xFFFF6B9D), const Color(0xFFC239B3)],
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildGradientStatCard(
                  Icons.access_time,
                  progress.formattedDuration,
                  'Total Time',
                  [const Color(0xFF4FACFE), const Color(0xFF00F2FE)],
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildGradientStatCard(
                  Icons.emoji_events,
                  progress.achievementsUnlocked.toString(),
                  'Badges',
                  [const Color(0xFFFFD700), const Color(0xFFFFAA00)],
                ),
              ),
            ],
          ),

          // Weekly Activity Chart
          if (weekly != null) ...[
            const SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Weekly Activity',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                    color: AppColors.textPrimary,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppColors.primary.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '${weekly.total} this week',
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: AppColors.primary,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            _buildWeeklyChart(weekly),
          ],
        ],
      ),
    );
  }

  Widget _buildGradientStatCard(IconData icon, String value, String label, List<Color> gradientColors) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: gradientColors,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: gradientColors[0].withValues(alpha: 0.3),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          Icon(icon, color: Colors.white, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w900,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            label,
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w600,
              color: Colors.white.withValues(alpha: 0.9),
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem(IconData icon, String value, String label, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w800,
              color: color,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            label,
            style: const TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: AppColors.textSecondary,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildWeeklyChart(WeeklyActivity weekly) {
    final days = [
      ('M', weekly.monday),
      ('T', weekly.tuesday),
      ('W', weekly.wednesday),
      ('T', weekly.thursday),
      ('F', weekly.friday),
      ('S', weekly.saturday),
      ('S', weekly.sunday),
    ];

    final maxSessions = weekly.maxSessions > 0 ? weekly.maxSessions : 1;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: days.map((day) {
          final height = (day.$2 / maxSessions) * 60;
          final isActive = day.$2 > 0;

          return Column(
            children: [
              // Bar
              Container(
                width: 36,
                height: 60,
                alignment: Alignment.bottomCenter,
                child: Container(
                  width: 36,
                  height: height.clamp(6.0, 60.0),
                  decoration: BoxDecoration(
                    gradient: isActive
                      ? const LinearGradient(
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                          colors: [
                            AppColors.primary,
                            AppColors.secondary,
                          ],
                        )
                      : null,
                    color: isActive ? null : AppColors.divider,
                    borderRadius: BorderRadius.circular(8),
                    boxShadow: isActive ? [
                      BoxShadow(
                        color: AppColors.primary.withValues(alpha: 0.3),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ] : null,
                  ),
                ),
              ),
              const SizedBox(height: 8),
              // Day label
              Text(
                day.$1,
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  color: isActive
                    ? AppColors.textPrimary
                    : AppColors.textSecondary,
                ),
              ),
            ],
          );
        }).toList(),
      ),
    );
  }
}
