// import 'package:flutter/material.dart';
// import 'package:serenity/services/emergency_service.dart';

// /// Emergency Confirmation Dialog
// /// Shown when crisis detected to user for confirmation before sending alert
// class EmergencyConfirmationDialog extends StatefulWidget {
//   final double riskScore;
//   final String crisisReason;
//   final List<EmergencyContact> contacts;
//   final Function(EmergencyContact)? onConfirm;
//   final VoidCallback? onCancel;

//   const EmergencyConfirmationDialog({
//     Key? key,
//     required this.riskScore,
//     required this.crisisReason,
//     required this.contacts,
//     this.onConfirm,
//     this.onCancel,
//   }) : super(key: key);

//   @override
//   State<EmergencyConfirmationDialog> createState() =>
//       _EmergencyConfirmationDialogState();
// }

// class _EmergencyConfirmationDialogState
//     extends State<EmergencyConfirmationDialog> {
//   late EmergencyContact? _selectedContact;
//   bool _isLoading = false;

//   @override
//   void initState() {
//     super.initState();
//     // Pre-select first contact if available
//     _selectedContact =
//         widget.contacts.isNotEmpty ? widget.contacts.first : null;
//   }

//   @override
//   Widget build(BuildContext context) {
//     final emergencyService = EmergencyService();
//     final crisisLevel = emergencyService.getCrisisLevel(widget.riskScore);
//     final riskPercent = emergencyService.formatRiskScore(widget.riskScore);

//     return AlertDialog(
//       backgroundColor: Colors.red.shade50,
//       title: Column(
//         children: [
//           Icon(Icons.warning_rounded, size: 40, color: Colors.red.shade700),
//           SizedBox(height: 12),
//           Text(
//             'CRISIS ALERT DETECTED',
//             style: TextStyle(
//               color: Colors.red.shade700,
//               fontWeight: FontWeight.bold,
//               fontSize: 18,
//             ),
//           ),
//         ],
//       ),
//       content: SingleChildScrollView(
//         child: Column(
//           mainAxisSize: MainAxisSize.min,
//           crossAxisAlignment: CrossAxisAlignment.start,
//           children: [
//             // Risk Summary
//             Container(
//               padding: EdgeInsets.all(12),
//               decoration: BoxDecoration(
//                 color: Colors.red.shade100,
//                 borderRadius: BorderRadius.circular(8),
//                 border: Border.all(color: Colors.red.shade300),
//               ),
//               child: Column(
//                 crossAxisAlignment: CrossAxisAlignment.start,
//                 children: [
//                   _buildRiskRow('Crisis Level', crisisLevel, Colors.red),
//                   SizedBox(height: 8),
//                   _buildRiskRow('Risk Score', riskPercent, Colors.orange),
//                   SizedBox(height: 8),
//                   _buildRiskRow(
//                       'Reason', widget.crisisReason, Colors.red.shade700),
//                 ],
//               ),
//             ),
//             SizedBox(height: 16),

//             // Contact Selection
//             Text(
//               'Notify Emergency Contact:',
//               style: TextStyle(
//                 fontWeight: FontWeight.bold,
//                 fontSize: 14,
//               ),
//             ),
//             SizedBox(height: 8),

//             if (widget.contacts.isNotEmpty)
//               DropdownButton<EmergencyContact>(
//                 isExpanded: true,
//                 value: _selectedContact,
//                 items: widget.contacts.map((contact) {
//                   return DropdownMenuItem(
//                     value: contact,
//                     child: Text(
//                       '${contact.contactName} (${contact.relationship})',
//                       style: TextStyle(fontSize: 14),
//                     ),
//                   );
//                 }).toList(),
//                 onChanged: (value) {
//                   if (value != null) {
//                     setState(() => _selectedContact = value);
//                   }
//                 },
//               )
//             else
//               Container(
//                 padding: EdgeInsets.all(12),
//                 decoration: BoxDecoration(
//                   color: Colors.amber.shade100,
//                   borderRadius: BorderRadius.circular(8),
//                 ),
//                 child: Row(
//                   children: [
//                     Icon(Icons.info_rounded, color: Colors.amber.shade700),
//                     SizedBox(width: 12),
//                     Expanded(
//                       child: Text(
//                         'No emergency contacts configured.\nPlease add contacts in settings.',
//                         style: TextStyle(
//                           color: Colors.amber.shade900,
//                           fontSize: 12,
//                         ),
//                       ),
//                     ),
//                   ],
//                 ),
//               ),

//             SizedBox(height: 16),

//             // Info message
//             Container(
//               padding: EdgeInsets.all(12),
//               decoration: BoxDecoration(
//                 color: Colors.blue.shade50,
//                 borderRadius: BorderRadius.circular(8),
//               ),
//               child: Text(
//                 '⚕️ Crisis detected: We will send an emergency alert to your selected contact with your location and crisis details.',
//                 style: TextStyle(
//                   fontSize: 12,
//                   color: Colors.blue.shade900,
//                   height: 1.5,
//                 ),
//               ),
//             ),
//           ],
//         ),
//       ),
//       actions: [
//         // Cancel button
//         TextButton(
//           onPressed: _isLoading
//               ? null
//               : () {
//                   Navigator.pop(context);
//                   widget.onCancel?.call();
//                 },
//           child: Text(
//             'CANCEL',
//             style: TextStyle(
//               color: Colors.grey.shade600,
//               fontWeight: FontWeight.bold,
//             ),
//           ),
//         ),

//         // Send Alert button
//         ElevatedButton.icon(
//           onPressed:
//               widget.contacts.isEmpty || _isLoading || _selectedContact == null
//                   ? null
//                   : () async {
//                       setState(() => _isLoading = true);

//                       try {
//                         // Trigger alert (selectedContact is guaranteed non-null here)
//                         if (_selectedContact != null) {
//                           widget.onConfirm?.call(_selectedContact!);
//                         }

//                         // Show confirmation
//                         if (mounted) {
//                           ScaffoldMessenger.of(context).showSnackBar(
//                             SnackBar(
//                               content: Row(
//                                 children: [
//                                   Icon(Icons.check_circle, color: Colors.white),
//                                   SizedBox(width: 12),
//                                   Expanded(
//                                     child: Text(
//                                       'Alert sent to ${_selectedContact?.contactName ?? "Contact"}',
//                                       style: TextStyle(
//                                         color: Colors.white,
//                                         fontWeight: FontWeight.bold,
//                                       ),
//                                     ),
//                                   ),
//                                 ],
//                               ),
//                               backgroundColor: Colors.green.shade600,
//                               duration: Duration(seconds: 3),
//                             ),
//                           );
//                           Navigator.pop(context);
//                         }
//                       } catch (e) {
//                         if (mounted) {
//                           ScaffoldMessenger.of(context).showSnackBar(
//                             SnackBar(
//                               content: Text('Failed to send alert: $e'),
//                               backgroundColor: Colors.red.shade600,
//                             ),
//                           );
//                           setState(() => _isLoading = false);
//                         }
//                       }
//                     },
//           icon: _isLoading
//               ? SizedBox(
//                   width: 16,
//                   height: 16,
//                   child: CircularProgressIndicator(strokeWidth: 2),
//                 )
//               : Icon(Icons.send_rounded),
//           label: Text(
//             'SEND EMERGENCY ALERT',
//             style: TextStyle(fontWeight: FontWeight.bold),
//           ),
//           style: ElevatedButton.styleFrom(
//             backgroundColor: Colors.red.shade600,
//             foregroundColor: Colors.white,
//             padding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
//           ),
//         ),
//       ],
//     );
//   }

//   Widget _buildRiskRow(String label, String value, Color color) {
//     return Row(
//       mainAxisAlignment: MainAxisAlignment.spaceBetween,
//       children: [
//         Text(
//           label,
//           style: TextStyle(
//             fontWeight: FontWeight.w500,
//             fontSize: 13,
//           ),
//         ),
//         Text(
//           value,
//           style: TextStyle(
//             fontWeight: FontWeight.bold,
//             fontSize: 13,
//             color: color,
//           ),
//         ),
//       ],
//     );
//   }
// }
