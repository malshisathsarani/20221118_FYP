import 'package:flutter/material.dart';
import '../../../shared/presentation/widgets/custom_app_bar.dart';
import '../../../shared/presentation/widgets/bottom_nav_bar.dart';
import '../../../core/constants/app_colors.dart';
import 'breathing_bubble_screen.dart';
import 'calm_puzzle_screen.dart';
import 'drawing_game_screen.dart';
import 'mandala_coloring_screen.dart';

class ToolsScreen extends StatelessWidget {
  const ToolsScreen({super.key});

  void _navigateToTool(BuildContext context, String toolName) {
    Widget? screen;

    switch (toolName) {
      case 'Breathing Bubbles':
        screen = const BreathingBubbleScreen();
        break;
      case 'Calm Puzzle':
        screen = const CalmPuzzleScreen();
        break;
      case 'Drawing Game':
        screen = const DrawingGameScreen();
        break;
      case 'Mandala Coloring':
        screen = const MandalaColoringScreen();
        break;
      default:
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('$toolName coming soon!')),
        );
        return;
    }

    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => screen!),
    );
  }

  @override
  Widget build(BuildContext context) {
    final categories = [
      ToolCategory(
        id: 1,
        name: 'Breathing',
        icon: Icons.air,
        color: AppColors.primary,
        bgColor: AppColors.surface,
        tools: const ['Breathing Bubbles'],
      ),
      ToolCategory(
        id: 2,
        name: 'Creative',
        icon: Icons.palette,
        color: AppColors.accent,
        bgColor: AppColors.surface,
        tools: const ['Mandala Coloring', 'Drawing Game'],
      ),
      ToolCategory(
        id: 3,
        name: 'Puzzles',
        icon: Icons.extension,
        color: AppColors.secondary,
        bgColor: AppColors.surface,
        tools: const ['Calm Puzzle'],
      ),
    ];

    return Scaffold(
      appBar: const CustomAppBar(title: 'Wellness Tools'),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              AppColors.background,
              AppColors.surface,
              AppColors.surface,
            ],
          ),
        ),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Tool Cards
              ...categories.expand((category) => category.tools.map((tool) {
                return Container(
                  margin: const EdgeInsets.only(bottom: 16),
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: AppColors.surface,
                    borderRadius: BorderRadius.circular(20),
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
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              tool,
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.w700,
                                color: AppColors.textPrimary,
                              ),
                            ),
                            const SizedBox(height: 4),
                            const Row(
                              children: [
                                Icon(
                                  Icons.access_time,
                                  size: 14,
                                  color: AppColors.textSecondary,
                                ),
                                SizedBox(width: 4),
                                Text(
                                  '5-10 minutes',
                                  style: TextStyle(
                                    fontSize: 13,
                                    color: AppColors.textSecondary,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                      ElevatedButton(
                        onPressed: () => _navigateToTool(context, tool),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: category.color,
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          padding: const EdgeInsets.symmetric(
                            horizontal: 20,
                            vertical: 12,
                          ),
                          elevation: 0,
                        ),
                        child: const Text(
                          'Start',
                          style: TextStyle(
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                    ],
                  ),
                );
              })),
            ],
          ),
        ),
      ),
      bottomNavigationBar: const BottomNavBar(currentIndex: 2),
    );
  }
}

class ToolCategory {
  final int id;
  final String name;
  final IconData icon;
  final Color color;
  final Color bgColor;
  final List<String> tools;

  ToolCategory({
    required this.id,
    required this.name,
    required this.icon,
    required this.color,
    required this.bgColor,
    required this.tools,
  });
}
