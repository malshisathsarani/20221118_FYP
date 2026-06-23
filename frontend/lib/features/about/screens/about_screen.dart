import 'package:flutter/material.dart';
import '../../../shared/presentation/widgets/custom_app_bar.dart';

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const CustomAppBar(title: 'About Serenity'),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // App Icon/Logo
            Center(
              child: Container(
                width: 100,
                height: 100,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      Theme.of(context).primaryColor,
                      const Color(0xFF4DB8A8),
                    ],
                  ),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: const Icon(
                  Icons.favorite,
                  size: 50,
                  color: Colors.white,
                ),
              ),
            ),
            const SizedBox(height: 24),

            // App Name & Version
            Center(
              child: Column(
                children: [
                  Text(
                    'Serenity',
                    style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Version 1.0.0',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.grey,
                        ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),

            // Introduction
            const Text(
              'Serenity is an AI-powered mental wellness companion designed to provide emotional support, crisis awareness, and personalized guidance in a safe and compassionate environment.',
              style: TextStyle(fontSize: 16, height: 1.5),
            ),
            const SizedBox(height: 16),
            const Text(
              'Unlike traditional chatbots, Serenity uses multi-modal intelligence to understand both what you say and how you say it. By analyzing text and voice signals, Serenity can better recognize emotional distress, stress, anxiety, and potential crisis situations at an earlier stage.',
              style: TextStyle(fontSize: 16, height: 1.5),
            ),
            const SizedBox(height: 32),

            // Key Features
            Text(
              'Key Features',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 16),

            _buildFeatureCard(
              icon: Icons.psychology,
              color: const Color(0xFF4DB8A8),
              title: 'Multi-Modal Crisis Detection',
              description:
                  'Analyzes both text and voice patterns for improved emotional understanding. Detects signs of distress, panic, sadness, or emotional crisis more accurately.',
            ),
            const SizedBox(height: 12),

            _buildFeatureCard(
              icon: Icons.favorite_border,
              color: const Color(0xFF7C3AED),
              title: 'Personalized Mental Wellness Support',
              description:
                  'Provides supportive conversations, coping strategies, and wellness recommendations tailored to individual needs.',
            ),
            const SizedBox(height: 12),

            _buildFeatureCard(
              icon: Icons.balance,
              color: const Color(0xFFF59E0B),
              title: 'Bias-Aware Learning',
              description:
                  'Learns from user feedback to improve fairness, inclusivity, and cultural sensitivity over time.',
            ),
            const SizedBox(height: 12),

            _buildFeatureCard(
              icon: Icons.shield,
              color: const Color(0xFFDC2626),
              title: 'Crisis Safety Protection',
              description:
                  'In high-risk situations, Serenity can initiate emergency support actions such as contacting a crisis hotline or notifying a trusted emergency contact, based on user settings and local regulations.',
            ),
            const SizedBox(height: 32),

            // Our Mission
            Text(
              'Our Mission',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 16),
            const Text(
              'Our mission is to make mental health support more accessible, responsive, and proactive by combining artificial intelligence with human-centered care. Serenity is designed to help users feel heard, supported, and connected whenever they need assistance.',
              style: TextStyle(fontSize: 16, height: 1.5),
            ),
            const SizedBox(height: 32),

            // Important Notice
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.orange.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: Colors.orange.withValues(alpha: 0.3),
                  width: 2,
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(
                        Icons.warning_amber,
                        color: Colors.orange,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'Important Notice',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: Colors.orange.shade800,
                            ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Serenity is not a replacement for licensed mental health professionals, medical treatment, or emergency services. If you are experiencing a mental health emergency, please contact local emergency services or a qualified healthcare professional immediately.',
                    style: TextStyle(
                      fontSize: 14,
                      height: 1.5,
                      color: Colors.orange.shade900,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),

            // Emergency Resources
            Text(
              'Emergency Resources',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 16),

            Card(
              child: Column(
                children: [
                  ListTile(
                    leading: const Icon(Icons.phone, color: Colors.red),
                    title: const Text('National Suicide Prevention Lifeline'),
                    subtitle: const Text('1-800-273-8255'),
                    trailing: const Icon(Icons.call),
                    onTap: () {
                      // In a real app, this would open the phone dialer
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Call: 1-800-273-8255'),
                        ),
                      );
                    },
                  ),
                  const Divider(height: 1),
                  ListTile(
                    leading: const Icon(Icons.message, color: Colors.blue),
                    title: const Text('Crisis Text Line'),
                    subtitle: const Text('Text HOME to 741741'),
                    trailing: const Icon(Icons.sms),
                    onTap: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Text HOME to 741741'),
                        ),
                      );
                    },
                  ),
                  const Divider(height: 1),
                  ListTile(
                    leading: const Icon(Icons.emergency, color: Colors.red),
                    title: const Text('Emergency Services'),
                    subtitle: const Text('911 (US) or local emergency number'),
                    trailing: const Icon(Icons.call),
                    onTap: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Call 911 for emergencies'),
                          backgroundColor: Colors.red,
                        ),
                      );
                    },
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),

            // Footer
            Center(
              child: Column(
                children: [
                  Text(
                    'Made with ❤️ for mental wellness',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.grey,
                        ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '© 2026 Serenity. All rights reserved.',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.grey,
                        ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildFeatureCard({
    required IconData icon,
    required Color color,
    required String title,
    required String description,
  }) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                icon,
                color: color,
                size: 28,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    description,
                    style: const TextStyle(
                      fontSize: 14,
                      height: 1.5,
                      color: Colors.grey,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
