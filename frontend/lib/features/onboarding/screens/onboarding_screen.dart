import 'package:flutter/material.dart';
import '../../../core/constants/app_colors.dart';


class OnboardingScreen extends StatefulWidget {
  final int initialStep;

  const OnboardingScreen({super.key, this.initialStep = 0});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  late int currentStep;

  final List<OnboardingStep> steps = [
    OnboardingStep(
      icon: Icons.favorite,
      title: 'You are not alone',
      description:
          'Join thousands finding peace and support through their mental health journey.',
    ),
    OnboardingStep(
      icon: Icons.bar_chart,
      title: 'Track how you feel',
      description:
          'Daily check-ins help you understand patterns and celebrate progress.',
    ),
    OnboardingStep(
      icon: Icons.chat_bubble,
      title: 'Get support anytime',
      description:
          'Chat with our AI assistant 24/7 for guidance, exercises, and compassionate listening.',
    ),
  ];

  @override
  void initState() {
    super.initState();
    currentStep = widget.initialStep;
  }

  void handleNext() {
    if (currentStep < steps.length - 1) {
      setState(() => currentStep++);
      Navigator.pushNamed(context, '/onboarding/$currentStep');
    } else {
      Navigator.pushNamed(context, '/signin');
    }
  }

  void handleSkip() {
    Navigator.pushNamed(context, '/signin');
  }

  @override
  Widget build(BuildContext context) {
    final step = steps[currentStep];

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          color: AppColors.background,
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Skip button
              Padding(
                padding: const EdgeInsets.all(16),
                child: Align(
                  alignment: Alignment.centerRight,
                  child: TextButton(
                    onPressed: handleSkip,
                    child: Text(
                      'Skip',
                      style: TextStyle(
                        color: Theme.of(context).textTheme.bodySmall?.color,
                      ),
                    ),
                  ),
                ),
              ),

              // Content
              Expanded(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      width: 128,
                      height: 128,
                      decoration: BoxDecoration(
                        color: Theme.of(context).primaryColor.withValues(alpha:0.1),
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        step.icon,
                        size: 64,
                        color: Theme.of(context).primaryColor,
                      ),
                    ),
                    const SizedBox(height: 32),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 32),
                      child: Text(
                        step.title,
                        style: Theme.of(context).textTheme.displaySmall,
                        textAlign: TextAlign.center,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 32),
                      child: Text(
                        step.description,
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color:
                                  Theme.of(context).textTheme.bodySmall?.color,
                            ),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ],
                ),
              ),

              // Bottom section
              Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  children: [
                    // Progress dots
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: List.generate(steps.length, (index) {
                        return AnimatedContainer(
                          duration: const Duration(milliseconds: 300),
                          margin: const EdgeInsets.symmetric(horizontal: 4),
                          width: index == currentStep ? 32 : 8,
                          height: 8,
                          decoration: BoxDecoration(
                            color: index == currentStep
                                ? Theme.of(context).primaryColor
                                : Theme.of(context).dividerColor,
                            borderRadius: BorderRadius.circular(4),
                          ),
                        );
                      }),
                    ),
                    const SizedBox(height: 24),

                    // CTA Button
                    SizedBox(
                      width: double.infinity,
                      height: 48,
                      child: ElevatedButton(
                        onPressed: handleNext,
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              currentStep == steps.length - 1
                                  ? 'Get Started'
                                  : 'Continue',
                            ),
                            const SizedBox(width: 8),
                            const Icon(Icons.arrow_forward, size: 20),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class OnboardingStep {
  final IconData icon;
  final String title;
  final String description;

  OnboardingStep({
    required this.icon,
    required this.title,
    required this.description,
  });
}
