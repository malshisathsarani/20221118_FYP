import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:universal_html/html.dart' as html;

import '../../../shared/presentation/widgets/custom_app_bar.dart';
import '../../../shared/presentation/widgets/bottom_nav_bar.dart';
import '../../../core/services/user_service.dart';
import '../../../core/constants/app_colors.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final UserService _userService = UserService();

  bool _loading = true;

  Map<String, dynamic>? _userData;
  Map<String, dynamic>? _userStats;

  @override
  void initState() {
    super.initState();
    _loadUserData();
  }

  Future<void> _loadUserData() async {
    try {
      final user = await _userService.getCurrentUser();
      final stats = await _userService.getUserStats();

      setState(() {
        _userData = user;
        _userStats = stats;
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  String _getInitials(String name) {
    final parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    }
    return name.isNotEmpty ? name.substring(0, 1).toUpperCase() : 'U';
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return Scaffold(
        appBar: const CustomAppBar(title: 'Profile & Settings'),
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
          child: const Center(
            child: CircularProgressIndicator(color: AppColors.primary),
          ),
        ),
        bottomNavigationBar: const BottomNavBar(currentIndex: 3),
      );
    }

    final userName = _userData?['full_name'] ?? _userData?['username'] ?? 'User';
    final userEmail = _userData?['email'] ?? 'No email';
    final initials = _getInitials(userName);

    return Scaffold(
      appBar: const CustomAppBar(title: 'Profile & Settings'),
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
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
            // User info - NOW WITH REAL DATA
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.divider, width: 1),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.05),
                    blurRadius: 10,
                    spreadRadius: 0,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 32,
                    backgroundColor: AppColors.primary,
                    child: Text(
                      initials,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          userName,
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: AppColors.textPrimary,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          userEmail,
                          style: const TextStyle(
                            fontSize: 14,
                            color: AppColors.textSecondary,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Mental Health Statistics
            _buildStatsCard(),
            const SizedBox(height: 24),

            // Emergency Contacts Quick Access
            _buildEmergencyContactsCard(),
            const SizedBox(height: 24),

            // Privacy & Security
            const Text(
              'Privacy & Security',
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: AppColors.textSecondary,
                letterSpacing: 0.5,
              ),
            ),
            const SizedBox(height: 12),
            Container(
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.divider, width: 1),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.05),
                    blurRadius: 10,
                    spreadRadius: 0,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                children: [
                  ListTile(
                    leading: const Icon(Icons.download, color: AppColors.primary),
                    title: const Text('Export my data', style: TextStyle(color: AppColors.textPrimary)),
                    subtitle: const Text('Download all your data', style: TextStyle(color: AppColors.textSecondary)),
                    trailing: const Icon(Icons.chevron_right, color: AppColors.textSecondary),
                    onTap: _exportUserData,
                  ),
                  const Divider(height: 1, color: AppColors.divider),
                  ListTile(
                    leading: const Icon(Icons.delete_forever, color: AppColors.error),
                    title: const Text('Delete account', style: TextStyle(color: AppColors.textPrimary)),
                    subtitle: const Text('Permanently delete all data', style: TextStyle(color: AppColors.textSecondary)),
                    trailing: const Icon(Icons.chevron_right, color: AppColors.textSecondary),
                    onTap: _showDeleteAccountDialog,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // About
            const Text(
              'About',
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: AppColors.textSecondary,
                letterSpacing: 0.5,
              ),
            ),
            const SizedBox(height: 12),
            Container(
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.divider, width: 1),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.05),
                    blurRadius: 10,
                    spreadRadius: 0,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: ListTile(
                leading: const Icon(Icons.info, color: AppColors.primary),
                title: const Text('About Serenity', style: TextStyle(color: AppColors.textPrimary)),
                subtitle: const Text('Learn more about our mission', style: TextStyle(color: AppColors.textSecondary)),
                trailing: const Icon(Icons.chevron_right, color: AppColors.textSecondary),
                onTap: () {
                  Navigator.pushNamed(context, '/about');
                },
              ),
            ),
            const SizedBox(height: 24),

            // Logout
            SizedBox(
              width: double.infinity,
              child: OutlinedButton(
                onPressed: () => Navigator.pushNamed(context, '/signin'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: AppColors.error,
                  side: const BorderSide(color: AppColors.error, width: 1.5),
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.logout),
                    SizedBox(width: 8),
                    Text('Log out', style: TextStyle(fontWeight: FontWeight.w600)),
                  ],
                ),
              ),
            ),
            ],
          ),
        ),
      ),
      bottomNavigationBar: const BottomNavBar(currentIndex: 3),
    );
  }

  Widget _buildStatsCard() {
    final totalChats = _userStats?['total_chats'] ?? 0;
    final crisisEvents = _userStats?['crisis_events'] ?? 0;
    final toolsUsed = _userStats?['tools_used'] ?? 0;
    final daysActive = _userStats?['days_active'] ?? 0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.only(left: 4, bottom: 12),
          child: Text(
            'Your Activity',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: AppColors.textPrimary,
            ),
          ),
        ),
        Row(
          children: [
            Expanded(
              child: _buildCompactStatCard(
                Icons.chat_bubble_outline,
                '$totalChats',
                'Chats',
                AppColors.primary,
                const Color(0xFFE0F7F6),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: _buildCompactStatCard(
                Icons.warning_amber_outlined,
                '$crisisEvents',
                'Alerts',
                const Color(0xFFF59E0B),
                const Color(0xFFFEF3C7),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: _buildCompactStatCard(
                Icons.brush_outlined,
                '$toolsUsed',
                'Tools',
                AppColors.secondary,
                const Color(0xFFE8F5E9),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: _buildCompactStatCard(
                Icons.calendar_today_outlined,
                '$daysActive',
                'Days',
                AppColors.accent,
                const Color(0xFFEDE9FE),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildCompactStatCard(IconData icon, String value, String label, Color iconColor, Color bgColor) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.divider, width: 1),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            spreadRadius: 0,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: bgColor,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: iconColor, size: 20),
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: const TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.bold,
              color: AppColors.textPrimary,
              height: 1,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: const TextStyle(
              fontSize: 11,
              color: AppColors.textSecondary,
              fontWeight: FontWeight.w500,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildEmergencyContactsCard() {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.divider, width: 1),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            spreadRadius: 0,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: ListTile(
        leading: const Icon(Icons.emergency_outlined, color: AppColors.error),
        title: const Text('Emergency Contacts', style: TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.w600)),
        subtitle: const Text('Manage your crisis alert contacts', style: TextStyle(color: AppColors.textSecondary)),
        trailing: const Icon(Icons.chevron_right, color: AppColors.textSecondary),
        onTap: () {
          Navigator.pushNamed(context, '/crisis');
        },
      ),
    );
  }


  Future<void> _exportUserData() async {
    // Show confirmation dialog first
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppColors.surface,
        title: const Text('Export Data?', style: TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.bold)),
        content: const Text(
          'This will download all your data including:\n\n'
          '• Profile information\n'
          '• Chat history\n'
          '• Crisis events\n'
          '• Emergency contacts\n'
          '• Activity statistics\n\n'
          'The data will be saved as an HTML file that you can view in your browser or print to PDF.',
          style: TextStyle(color: AppColors.textPrimary),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            style: TextButton.styleFrom(foregroundColor: AppColors.textSecondary),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(foregroundColor: AppColors.primary),
            child: const Text('Export', style: TextStyle(fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    if (!mounted) return;

    try {
      // Show loading dialog
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => const Center(
          child: CircularProgressIndicator(color: AppColors.primary),
        ),
      );

      final data = await _userService.exportUserData();

      if (!mounted) return;
      Navigator.pop(context); // Close loading

      // Create readable HTML report
      final htmlContent = _buildHtmlReport(data);

      // Create a downloadable HTML file
      final bytes = utf8.encode(htmlContent);
      final blob = html.Blob([bytes], 'text/html');
      final url = html.Url.createObjectUrlFromBlob(blob);

      // Create download link and trigger download
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      html.AnchorElement(href: url)
        ..setAttribute('download', 'Serenity_Data_Export_$timestamp.html')
        ..click();

      // Clean up
      html.Url.revokeObjectUrl(url);

      // Show success message
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('✅ Data exported! Open the HTML file in your browser or print to PDF.'),
          backgroundColor: AppColors.success,
          duration: Duration(seconds: 4),
        ),
      );
    } catch (e) {
      if (!mounted) return;
      Navigator.pop(context); // Close loading

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Export failed: $e'),
          backgroundColor: AppColors.error,
        ),
      );
    }
  }

  String _buildHtmlReport(Map<String, dynamic> data) {
    final userProfile = data['user_profile'] ?? {};
    final chats = (data['chats'] as List?) ?? [];
    final contacts = (data['emergency_contacts'] as List?) ?? [];
    final feedback = (data['feedback'] as List?) ?? [];
    final exportDate = data['export_date'] ?? '';

    // Count statistics
    final totalChats = chats.length;
    final crisisEvents = chats.where((c) => c['is_crisis'] == 1).length;
    final totalFeedback = feedback.length;

    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Serenity Mental Health Report</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Georgia', 'Times New Roman', serif;
            line-height: 1.8;
            color: #000000;
            background: white;
            padding: 40px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
        }
        .header {
            border-bottom: 3px solid #000000;
            padding-bottom: 20px;
            margin-bottom: 40px;
        }
        .header h1 {
            font-size: 28px;
            font-weight: normal;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 10px;
        }
        .header .subtitle {
            font-size: 14px;
            color: #555555;
            font-style: italic;
        }
        .header .export-date {
            font-size: 11px;
            color: #777777;
            margin-top: 8px;
        }
        .section {
            margin-bottom: 50px;
            page-break-inside: avoid;
        }
        .section-title {
            font-size: 18px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #000000;
        }
        .info-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .info-table td {
            padding: 12px 0;
            border-bottom: 1px solid #e0e0e0;
        }
        .info-table td:first-child {
            font-weight: bold;
            width: 200px;
            color: #333333;
        }
        .info-table td:last-child {
            color: #000000;
        }
        .stats-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .stats-table th,
        .stats-table td {
            padding: 14px;
            text-align: left;
            border: 1px solid #cccccc;
        }
        .stats-table th {
            background: #f5f5f5;
            font-weight: bold;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 0.5px;
        }
        .stats-table td {
            font-size: 14px;
        }
        .contact-item {
            padding: 16px 0;
            border-bottom: 1px solid #e0e0e0;
        }
        .contact-item:last-child {
            border-bottom: none;
        }
        .contact-name {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 4px;
        }
        .contact-details {
            font-size: 14px;
            color: #555555;
        }
        .chat-item {
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #cccccc;
            page-break-inside: avoid;
        }
        .chat-header {
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid #e0e0e0;
        }
        .chat-date {
            font-size: 12px;
            color: #666666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .chat-meta {
            font-size: 11px;
            color: #888888;
            margin-top: 4px;
        }
        .chat-message,
        .chat-response {
            padding: 12px 0;
            font-family: 'Arial', sans-serif;
            font-size: 13px;
            line-height: 1.6;
        }
        .chat-label {
            font-size: 10px;
            font-weight: bold;
            text-transform: uppercase;
            color: #666666;
            margin-bottom: 6px;
            letter-spacing: 0.5px;
        }
        .footer {
            margin-top: 60px;
            padding-top: 20px;
            border-top: 2px solid #000000;
            text-align: center;
            font-size: 11px;
            color: #888888;
        }
        .confidential {
            background: #f9f9f9;
            border: 2px solid #cccccc;
            padding: 16px;
            margin: 30px 0;
            font-size: 12px;
            text-align: center;
        }
        .confidential strong {
            display: block;
            margin-bottom: 8px;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        @media print {
            body { padding: 20px; }
            .no-print { display: none !important; }
        }
        .print-btn {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #000000;
            color: white;
            border: none;
            padding: 12px 24px;
            cursor: pointer;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 11px;
        }
        .print-btn:hover {
            background: #333333;
        }
    </style>
</head>
<body>
    <button class="print-btn no-print" onclick="window.print()">Print to PDF</button>

    <div class="container">
        <div class="header">
            <h1>Serenity Mental Health Report</h1>
            <div class="subtitle">Confidential Patient Data Export</div>
            <div class="export-date">Generated: ${DateTime.parse(exportDate).toString().split('.')[0]}</div>
        </div>

        <div class="confidential">
            <strong>Confidential Document</strong>
            This report contains sensitive mental health information. Handle with care and in accordance with privacy regulations.
        </div>

        <!-- Profile Section -->
        <div class="section">
            <h2 class="section-title">Profile Information</h2>
            <table class="info-table">
                <tr>
                    <td>Full Name</td>
                    <td>${userProfile['full_name'] ?? 'N/A'}</td>
                </tr>
                <tr>
                    <td>Email Address</td>
                    <td>${userProfile['email'] ?? 'N/A'}</td>
                </tr>
                <tr>
                    <td>Username</td>
                    <td>${userProfile['username'] ?? 'N/A'}</td>
                </tr>
                <tr>
                    <td>User ID</td>
                    <td>#${userProfile['id']}</td>
                </tr>
                <tr>
                    <td>Account Created</td>
                    <td>${userProfile['created_at']?.toString().split('T')[0] ?? 'N/A'}</td>
                </tr>
            </table>
        </div>

        <!-- Statistics Section -->
        <div class="section">
            <h2 class="section-title">Activity Statistics</h2>
            <table class="stats-table">
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th style="text-align: center;">Count</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Total Conversations</td>
                        <td style="text-align: center;"><strong>$totalChats</strong></td>
                        <td>Number of chat sessions initiated</td>
                    </tr>
                    <tr>
                        <td>Crisis Events Detected</td>
                        <td style="text-align: center;"><strong>$crisisEvents</strong></td>
                        <td>High-risk conversations flagged</td>
                    </tr>
                    <tr>
                        <td>Feedback Submissions</td>
                        <td style="text-align: center;"><strong>$totalFeedback</strong></td>
                        <td>User feedback provided to system</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Emergency Contacts -->
        <div class="section">
            <h2 class="section-title">Emergency Contacts</h2>
            ${contacts.isEmpty ? '<p style="color: #666666; font-style: italic;">No emergency contacts configured.</p>' : contacts.map((contact) => '''
            <div class="contact-item">
                <div class="contact-name">${contact['name']}</div>
                <div class="contact-details">Phone: ${contact['phone']} ${contact['relationship_type'] != null ? '• Relationship: ${contact['relationship_type']}' : ''} ${contact['is_primary'] == true ? '• PRIMARY CONTACT' : ''}</div>
            </div>
            ''').join('')}
        </div>

        <!-- Chat History -->
        <div class="section">
            <h2 class="section-title">Conversation History</h2>
            <p style="margin-bottom: 20px; color: #666666;">Total Conversations: ${chats.length}${chats.length > 50 ? ' (showing most recent 50)' : ''}</p>
            ${chats.isEmpty ? '<p style="color: #666666; font-style: italic;">No conversation history available.</p>' : chats.reversed.take(50).map((chat) {
              final isCrisis = chat['is_crisis'] == 1;
              final emotion = chat['detected_emotion'] ?? 'unknown';
              final date = chat['created_at']?.toString().split('T')[0] ?? 'N/A';
              final time = chat['created_at']?.toString().split('T')[1].split('.')[0] ?? 'N/A';

              return '''
              <div class="chat-item">
                  <div class="chat-header">
                      <div class="chat-date">$date at $time</div>
                      <div class="chat-meta">Emotion: ${emotion.toUpperCase()} • Status: ${isCrisis ? 'CRISIS DETECTED' : 'SAFE'}</div>
                  </div>
                  <div class="chat-message">
                      <div class="chat-label">Patient Message:</div>
                      ${chat['message'] ?? ''}
                  </div>
                  <div class="chat-response">
                      <div class="chat-label">System Response:</div>
                      ${chat['response']?.toString().replaceAll('\n', '<br>') ?? ''}
                  </div>
              </div>
              ''';
            }).join('')}
        </div>

        <div class="footer">
            <p><strong>SERENITY MENTAL HEALTH CHATBOT</strong></p>
            <p style="margin-top: 8px;">This data export is provided in accordance with GDPR Article 20 (Right to Data Portability).</p>
            <p style="margin-top: 8px;">Document generated on ${DateTime.parse(exportDate).toString().split('.')[0]}</p>
            <p style="margin-top: 12px;">For inquiries: serenity@mentalhealth.com</p>
        </div>
    </div>
</body>
</html>
''';
  }

  Future<void> _showDeleteAccountDialog() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppColors.surface,
        title: const Text('Delete Account?', style: TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.bold)),
        content: const Text(
          'This will permanently delete:\n\n'
          '• All chat history\n'
          '• Crisis event records\n'
          '• Emergency contacts\n'
          '• Usage statistics\n'
          '• Profile information\n\n'
          'This action cannot be undone.',
          style: TextStyle(color: AppColors.textPrimary),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            style: TextButton.styleFrom(foregroundColor: AppColors.textSecondary),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(foregroundColor: AppColors.error),
            child: const Text('Delete Forever', style: TextStyle(fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      if (!mounted) return;

      try {
        // Show loading
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (context) => const Center(
            child: CircularProgressIndicator(color: AppColors.primary),
          ),
        );

        await _userService.deleteAccount();
        await _userService.logout();

        if (!mounted) return;
        Navigator.pop(context); // Close loading

        // Navigate to sign in
        Navigator.pushNamedAndRemoveUntil(
          context,
          '/signin',
          (route) => false,
        );
      } catch (e) {
        if (!mounted) return;
        Navigator.pop(context); // Close loading

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Delete failed: $e'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    }
  }
}
