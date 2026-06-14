import 'package:flutter/material.dart';

class SafetyBanner extends StatelessWidget {
  final VoidCallback onGetHelp;

  const SafetyBanner({
    super.key,
    required this.onGetHelp,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        border: Border.all(color: Colors.red.shade200),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(Icons.warning, color: Colors.red.shade700),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Crisis Detected',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.red.shade900,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'If you\'re in immediate danger, please seek help.',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.red.shade700,
                  ),
                ),
              ],
            ),
          ),
          TextButton(
            onPressed: onGetHelp,
            child: const Text('Get Help'),
          ),
        ],
      ),
    );
  }
}
