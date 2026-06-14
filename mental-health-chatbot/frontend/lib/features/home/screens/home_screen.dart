import 'package:flutter/material.dart';
import '../../../core/constants/app_colors.dart';
import 'dart:math' as math;

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with TickerProviderStateMixin {
  late List<AnimationController> _controllers;
  late List<Animation<double>> _animations;

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
          // Animated background
          Container(
            decoration: const BoxDecoration(
              color: AppColors.background,
            ),
            child: Stack(
              children: [
                // Floating circles
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
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Header
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Welcome Back!',
                            style: TextStyle(
                              fontSize: 32,
                              fontWeight: FontWeight.w800,
                              color: AppColors.textPrimary,
                              letterSpacing: -1,
                            ),
                          ),
                          const SizedBox(height: 4),
                          const Text(
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
                              color: AppColors.primary.withOpacity(0.3),
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
                  const SizedBox(height: 32),

                  // Feature Cards
                  Expanded(
                    child: Column(
                      children: [
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
                        Expanded(
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
                      ],
                    ),
                  ),
                ],
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
      AppColors.primary.withOpacity(0.08),
      AppColors.secondary.withOpacity(0.08),
      AppColors.accent.withOpacity(0.08),
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
                  color: colors[index % colors.length].withOpacity(0.3),
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
              color.withOpacity(0.8),
            ],
          ),
          borderRadius: BorderRadius.circular(24),
          boxShadow: [
            BoxShadow(
              color: color.withOpacity(0.3),
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
                color: Colors.white.withOpacity(0.2),
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
                      color: Colors.white.withOpacity(0.9),
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
              color: Colors.black.withOpacity(0.05),
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
                color: color.withOpacity(0.1),
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
}
