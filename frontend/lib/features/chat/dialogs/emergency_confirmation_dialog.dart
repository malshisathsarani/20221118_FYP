import 'package:flutter/material.dart';
import '../../../core/models/emergency_contact.dart';

/// Emergency Confirmation Dialog
/// Shown when crisis detected to user for confirmation before sending alert
class EmergencyConfirmationDialog extends StatefulWidget {
  final double riskScore;
  final String crisisReason;
  final List<EmergencyContactModel> contacts;
  final Function(EmergencyContactModel)? onConfirm;
  final VoidCallback? onCancel;
  final int countdownSeconds;

  const EmergencyConfirmationDialog({
    super.key,
    required this.riskScore,
    required this.crisisReason,
    required this.contacts,
    this.onConfirm,
    this.onCancel,
    this.countdownSeconds = 30,
  });

  @override
  State<EmergencyConfirmationDialog> createState() =>
      _EmergencyConfirmationDialogState();
}

class _EmergencyConfirmationDialogState
    extends State<EmergencyConfirmationDialog> {
  late EmergencyContactModel? _selectedContact;
  bool _isLoading = false;
  int _countdown = 30;
  bool _autoSendEnabled = true;

  @override
  void initState() {
    super.initState();
    _countdown = widget.countdownSeconds;
    // Pre-select first contact if available
    _selectedContact =
        widget.contacts.isNotEmpty ? widget.contacts.first : null;

    // Start countdown timer
    _startCountdown();
  }

  void _startCountdown() {
    Future.delayed(const Duration(seconds: 1), () {
      if (mounted && _countdown > 0 && _autoSendEnabled) {
        setState(() {
          _countdown--;
        });

        if (_countdown == 0 && _selectedContact != null) {
          // Auto-send alert when countdown reaches 0
          _sendAlert();
        } else {
          _startCountdown();
        }
      }
    });
  }

  void _sendAlert() async {
    if (_selectedContact == null || _isLoading) return;

    setState(() => _isLoading = true);

    try {
      // Trigger alert
      widget.onConfirm?.call(_selectedContact!);

      // Show confirmation
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.check_circle, color: Colors.white),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Alert sent to ${_selectedContact?.name ?? "Contact"}',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            backgroundColor: Colors.green.shade600,
            duration: const Duration(seconds: 3),
          ),
        );
        Navigator.pop(context);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to send alert: $e'),
            backgroundColor: Colors.red.shade600,
          ),
        );
        setState(() => _isLoading = false);
      }
    }
  }

  String _getCrisisLevel(double riskScore) {
    if (riskScore >= 0.85) return 'CRITICAL';
    if (riskScore >= 0.70) return 'HIGH';
    if (riskScore >= 0.45) return 'MODERATE';
    return 'LOW';
  }

  String _formatRiskScore(double riskScore) {
    return '${(riskScore * 100).toStringAsFixed(1)}%';
  }

  @override
  Widget build(BuildContext context) {
    final crisisLevel = _getCrisisLevel(widget.riskScore);
    final riskPercent = _formatRiskScore(widget.riskScore);

    return AlertDialog(
      backgroundColor: Colors.red.shade50,
      title: Column(
        children: [
          Icon(Icons.warning_rounded, size: 40, color: Colors.red.shade700),
          const SizedBox(height: 12),
          Text(
            'CRISIS ALERT DETECTED',
            style: TextStyle(
              color: Colors.red.shade700,
              fontWeight: FontWeight.bold,
              fontSize: 18,
            ),
          ),
          // Countdown timer
          if (_autoSendEnabled && _countdown > 0)
            Container(
              margin: const EdgeInsets.only(top: 12),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: Colors.orange.shade100,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: Colors.orange.shade400, width: 2),
              ),
              child: Text(
                'Auto-sending in $_countdown seconds',
                style: TextStyle(
                  color: Colors.orange.shade900,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
            ),
        ],
      ),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Risk Summary
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.red.shade100,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.red.shade300),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildRiskRow('Crisis Level', crisisLevel, Colors.red),
                  const SizedBox(height: 8),
                  _buildRiskRow('Risk Score', riskPercent, Colors.orange),
                  const SizedBox(height: 8),
                  _buildRiskRow(
                      'Reason', widget.crisisReason, Colors.red.shade700),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Contact Selection
            const Text(
              'Notify Emergency Contact:',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 8),

            if (widget.contacts.isNotEmpty)
              DropdownButton<EmergencyContactModel>(
                isExpanded: true,
                value: _selectedContact,
                items: widget.contacts.map((contact) {
                  return DropdownMenuItem(
                    value: contact,
                    child: Text(
                      '${contact.name} (${contact.relationshipType ?? "Contact"})',
                      style: const TextStyle(fontSize: 14),
                    ),
                  );
                }).toList(),
                onChanged: (value) {
                  if (value != null) {
                    setState(() => _selectedContact = value);
                  }
                },
              )
            else
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.amber.shade100,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(Icons.info_rounded, color: Colors.amber.shade700),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'No emergency contacts configured.\nPlease add contacts in settings.',
                        style: TextStyle(
                          color: Colors.amber.shade900,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ],
                ),
              ),

            const SizedBox(height: 16),

            // Info message
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                '⚕️ Crisis detected: We will send an emergency alert to your selected contact with your location and crisis details.',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.blue.shade900,
                  height: 1.5,
                ),
              ),
            ),
          ],
        ),
      ),
      actions: [
        // Cancel button (stops auto-send)
        TextButton(
          onPressed: _isLoading
              ? null
              : () {
                  setState(() => _autoSendEnabled = false);
                  Navigator.pop(context);
                  widget.onCancel?.call();
                },
          child: Text(
            'CANCEL',
            style: TextStyle(
              color: Colors.grey.shade600,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),

        // Send Alert button (manual send)
        ElevatedButton.icon(
          onPressed:
              widget.contacts.isEmpty || _isLoading || _selectedContact == null
                  ? null
                  : () {
                      setState(() => _autoSendEnabled = false);
                      _sendAlert();
                    },
          icon: _isLoading
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Icon(Icons.send_rounded),
          label: const Text(
            'SEND NOW',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.red.shade600,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          ),
        ),
      ],
    );
  }

  Widget _buildRiskRow(String label, String value, Color color) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Expanded(
          child: Text(
            label,
            style: const TextStyle(
              fontWeight: FontWeight.w500,
              fontSize: 13,
            ),
          ),
        ),
        const SizedBox(width: 8),
        Flexible(
          child: Text(
            value,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 13,
              color: color,
            ),
            textAlign: TextAlign.right,
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }

  @override
  void dispose() {
    _autoSendEnabled = false;
    super.dispose();
  }
}
