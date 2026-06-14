// import 'package:flutter/material.dart';
// import 'package:flutter_app/services/emergency_service.dart';

// /// Emergency Contacts Settings Screen
// /// Allows users to manage emergency contacts and consent settings
// class EmergencyContactsScreen extends StatefulWidget {
//   final int userId;

//   const EmergencyContactsScreen({
//     Key? key,
//     required this.userId,
//   }) : super(key: key);

//   @override
//   State<EmergencyContactsScreen> createState() =>
//       _EmergencyContactsScreenState();
// }

// class _EmergencyContactsScreenState extends State<EmergencyContactsScreen> {
//   final _emergencyService = EmergencyService();
//   late Future<List<EmergencyContact>> _contactsFuture;
//   late Future<UserSettings> _settingsFuture;

//   final _nameController = TextEditingController();
//   final _phoneController = TextEditingController();
//   String _selectedRelationship = 'family';

//   @override
//   void initState() {
//     super.initState();
//     _refreshData();
//   }

//   void _refreshData() {
//     setState(() {
//       _contactsFuture = _emergencyService.getEmergencyContacts(widget.userId);
//       _settingsFuture = _emergencyService.getUserSettings(widget.userId);
//     });
//   }

//   @override
//   void dispose() {
//     _nameController.dispose();
//     _phoneController.dispose();
//     super.dispose();
//   }

//   void _showAddContactDialog() {
//     showDialog(
//       context: context,
//       builder: (context) => AlertDialog(
//         title: Text('Add Emergency Contact'),
//         content: SingleChildScrollView(
//           child: Column(
//             mainAxisSize: MainAxisSize.min,
//             children: [
//               TextField(
//                 controller: _nameController,
//                 decoration: InputDecoration(
//                   labelText: 'Contact Name',
//                   hintText: 'e.g., Mom, Best Friend',
//                   border: OutlineInputBorder(),
//                 ),
//               ),
//               SizedBox(height: 12),
//               TextField(
//                 controller: _phoneController,
//                 decoration: InputDecoration(
//                   labelText: 'Phone Number',
//                   hintText: '+1234567890',
//                   border: OutlineInputBorder(),
//                 ),
//                 keyboardType: TextInputType.phone,
//               ),
//               SizedBox(height: 12),
//               DropdownButton<String>(
//                 isExpanded: true,
//                 value: _selectedRelationship,
//                 items: [
//                   'family',
//                   'friend',
//                   'doctor',
//                   'therapist',
//                   'emergency services'
//                 ]
//                     .map((rel) => DropdownMenuItem(
//                           value: rel,
//                           child: Text(rel.toUpperCase()),
//                         ))
//                     .toList(),
//                 onChanged: (value) {
//                   if (value != null) {
//                     setState(() => _selectedRelationship = value);
//                   }
//                 },
//               ),
//             ],
//           ),
//         ),
//         actions: [
//           TextButton(
//             onPressed: () => Navigator.pop(context),
//             child: Text('Cancel'),
//           ),
//           ElevatedButton(
//             onPressed: _iPhoneControllerEmpty() ? null : _addContact,
//             child: Text('Add Contact'),
//           ),
//         ],
//       ),
//     );
//   }

//   bool _iPhoneControllerEmpty() {
//     return _nameController.text.isEmpty || _phoneController.text.isEmpty;
//   }

//   void _addContact() async {
//     try {
//       await _emergencyService.addEmergencyContact(
//         userId: widget.userId,
//         contactName: _nameController.text,
//         phoneNumber: _phoneController.text,
//         relationship: _selectedRelationship,
//       );

//       _nameController.clear();
//       _phoneController.clear();
//       _selectedRelationship = 'family';

//       Navigator.pop(context);
//       _refreshData();

//       ScaffoldMessenger.of(context).showSnackBar(
//         SnackBar(
//           content: Text('Contact added successfully'),
//           backgroundColor: Colors.green,
//         ),
//       );
//     } catch (e) {
//       ScaffoldMessenger.of(context).showSnackBar(
//         SnackBar(
//           content: Text('Error adding contact: $e'),
//           backgroundColor: Colors.red,
//         ),
//       );
//     }
//   }

//   void _deleteContact(int contactId) async {
//     try {
//       await _emergencyService.deleteEmergencyContact(widget.userId, contactId);
//       _refreshData();

//       ScaffoldMessenger.of(context).showSnackBar(
//         SnackBar(
//           content: Text('Contact deleted'),
//           backgroundColor: Colors.orange,
//         ),
//       );
//     } catch (e) {
//       ScaffoldMessenger.of(context).showSnackBar(
//         SnackBar(
//           content: Text('Error deleting contact: $e'),
//           backgroundColor: Colors.red,
//         ),
//       );
//     }
//   }

//   @override
//   Widget build(BuildContext context) {
//     return Scaffold(
//       appBar: AppBar(
//         title: Text('Emergency Contacts'),
//         backgroundColor: Colors.red.shade600,
//         foregroundColor: Colors.white,
//       ),
//       body: SingleChildScrollView(
//         padding: EdgeInsets.all(16),
//         child: Column(
//           crossAxisAlignment: CrossAxisAlignment.start,
//           children: [
//             // Settings Section
//             _buildSettingsSection(),
//             SizedBox(height: 24),

//             // Contacts Section
//             _buildContactsSection(),
//           ],
//         ),
//       ),
//       floatingActionButton: FloatingActionButton(
//         onPressed: _showAddContactDialog,
//         backgroundColor: Colors.red.shade600,
//         child: Icon(Icons.add),
//         tooltip: 'Add Emergency Contact',
//       ),
//     );
//   }

//   Widget _buildSettingsSection() {
//     return Column(
//       crossAxisAlignment: CrossAxisAlignment.start,
//       children: [
//         Text(
//           'Settings & Consent',
//           style: TextStyle(
//             fontSize: 18,
//             fontWeight: FontWeight.bold,
//           ),
//         ),
//         SizedBox(height: 12),
//         FutureBuilder<UserSettings>(
//           future: _settingsFuture,
//           builder: (context, snapshot) {
//             if (snapshot.connectionState == ConnectionState.waiting) {
//               return Center(child: CircularProgressIndicator());
//             }

//             if (snapshot.hasError) {
//               return Text('Error loading settings: ${snapshot.error}');
//             }

//             final settings = snapshot.data!;

//             return Column(
//               children: [
//                 // Auto-alert toggle
//                 Card(
//                   child: SwitchListTile(
//                     title: Text('Auto-Alert Enabled'),
//                     subtitle:
//                         Text('Automatically send alerts on crisis detection'),
//                     value: settings.autoAlertEnabled,
//                     onChanged: (value) {
//                       settings.autoAlertEnabled = value;
//                       _emergencyService.updateUserSettings(
//                           widget.userId, settings);
//                       _refreshData();
//                     },
//                     activeColor: Colors.green,
//                   ),
//                 ),
//                 SizedBox(height: 8),

//                 // Auto-call toggle (REQUIRES EXPLICIT CONSENT)
//                 Card(
//                   child: SwitchListTile(
//                     title: Text('Auto-Call Enabled ⚠️'),
//                     subtitle: Text(
//                       'Automatically call emergency contact on crisis\n(Requires explicit consent)',
//                       style: TextStyle(color: Colors.red.shade700),
//                     ),
//                     value: settings.autoCallEnabled,
//                     onChanged: (value) {
//                       if (value) {
//                         _showAutoCallConsentDialog(settings);
//                       } else {
//                         settings.autoCallEnabled = false;
//                         _emergencyService.updateUserSettings(
//                             widget.userId, settings);
//                         _refreshData();
//                       }
//                     },
//                     activeColor: Colors.red.shade600,
//                   ),
//                 ),
//                 SizedBox(height: 8),

//                 // Crisis threshold
//                 Card(
//                   child: Padding(
//                     padding: EdgeInsets.all(16),
//                     child: Column(
//                       crossAxisAlignment: CrossAxisAlignment.start,
//                       children: [
//                         Row(
//                           mainAxisAlignment: MainAxisAlignment.spaceBetween,
//                           children: [
//                             Text(
//                               'Crisis Alert Threshold',
//                               style: TextStyle(fontWeight: FontWeight.bold),
//                             ),
//                             Text(
//                               '${(settings.crisisThreshold * 100).toInt()}%',
//                               style: TextStyle(
//                                 fontWeight: FontWeight.bold,
//                                 color: Colors.red,
//                               ),
//                             ),
//                           ],
//                         ),
//                         SizedBox(height: 12),
//                         Slider(
//                           value: settings.crisisThreshold,
//                           min: 0.3,
//                           max: 1.0,
//                           divisions: 7,
//                           onChanged: (value) {
//                             setState(() {
//                               settings.crisisThreshold = value;
//                             });
//                           },
//                           onChangeEnd: (value) {
//                             _emergencyService.updateUserSettings(
//                                 widget.userId, settings);
//                           },
//                           activeColor: Colors.red,
//                         ),
//                         SizedBox(height: 8),
//                         Text(
//                           'Lower value = more sensitive to crisis detection',
//                           style: TextStyle(fontSize: 12, color: Colors.grey),
//                         ),
//                       ],
//                     ),
//                   ),
//                 ),
//               ],
//             );
//           },
//         ),
//       ],
//     );
//   }

//   Widget _buildContactsSection() {
//     return Column(
//       crossAxisAlignment: CrossAxisAlignment.start,
//       children: [
//         Text(
//           'Your Emergency Contacts',
//           style: TextStyle(
//             fontSize: 18,
//             fontWeight: FontWeight.bold,
//           ),
//         ),
//         SizedBox(height: 12),
//         FutureBuilder<List<EmergencyContact>>(
//           future: _contactsFuture,
//           builder: (context, snapshot) {
//             if (snapshot.connectionState == ConnectionState.waiting) {
//               return Center(child: CircularProgressIndicator());
//             }

//             if (snapshot.hasError) {
//               return Text('Error loading contacts: ${snapshot.error}');
//             }

//             final contacts = snapshot.data ?? [];

//             if (contacts.isEmpty) {
//               return Container(
//                 padding: EdgeInsets.all(24),
//                 decoration: BoxDecoration(
//                   color: Colors.grey.shade100,
//                   borderRadius: BorderRadius.circular(8),
//                 ),
//                 child: Center(
//                   child: Column(
//                     children: [
//                       Icon(
//                         Icons.person_add_rounded,
//                         size: 48,
//                         color: Colors.grey.shade400,
//                       ),
//                       SizedBox(height: 12),
//                       Text(
//                         'No emergency contacts added yet',
//                         style: TextStyle(
//                           color: Colors.grey.shade600,
//                           fontSize: 16,
//                         ),
//                       ),
//                       SizedBox(height: 8),
//                       Text(
//                         'Tap + to add your first emergency contact',
//                         style: TextStyle(
//                           color: Colors.grey.shade500,
//                           fontSize: 12,
//                         ),
//                       ),
//                     ],
//                   ),
//                 ),
//               );
//             }

//             return ListView.builder(
//               shrinkWrap: true,
//               physics: NeverScrollableScrollPhysics(),
//               itemCount: contacts.length,
//               itemBuilder: (context, index) {
//                 final contact = contacts[index];
//                 return Card(
//                   margin: EdgeInsets.only(bottom: 8),
//                   child: ListTile(
//                     leading: CircleAvatar(
//                       backgroundColor: Colors.red.shade100,
//                       child: Icon(
//                         Icons.person_rounded,
//                         color: Colors.red.shade600,
//                       ),
//                     ),
//                     title: Text(contact.contactName),
//                     subtitle: Text(
//                       '${contact.phoneNumber} • ${contact.relationship ?? 'contact'}',
//                     ),
//                     trailing: IconButton(
//                       icon: Icon(Icons.delete, color: Colors.red),
//                       onPressed: () {
//                         showDialog(
//                           context: context,
//                           builder: (context) => AlertDialog(
//                             title: Text('Delete Contact?'),
//                             content: Text(
//                               'Are you sure you want to delete ${contact.contactName}?',
//                             ),
//                             actions: [
//                               TextButton(
//                                 onPressed: () => Navigator.pop(context),
//                                 child: Text('Cancel'),
//                               ),
//                               TextButton(
//                                 onPressed: () {
//                                   _deleteContact(contact.id);
//                                   Navigator.pop(context);
//                                 },
//                                 child: Text(
//                                   'Delete',
//                                   style: TextStyle(color: Colors.red),
//                                 ),
//                               ),
//                             ],
//                           ),
//                         );
//                       },
//                     ),
//                   ),
//                 );
//               },
//             );
//           },
//         ),
//       ],
//     );
//   }

//   void _showAutoCallConsentDialog(UserSettings settings) {
//     showDialog(
//       context: context,
//       builder: (context) => AlertDialog(
//         backgroundColor: Colors.red.shade50,
//         title: Text(
//           'Enable Automatic Emergency Calling?',
//           style: TextStyle(
//               color: Colors.red.shade700, fontWeight: FontWeight.bold),
//         ),
//         content: SingleChildScrollView(
//           child: Column(
//             mainAxisSize: MainAxisSize.min,
//             crossAxisAlignment: CrossAxisAlignment.start,
//             children: [
//               Container(
//                 padding: EdgeInsets.all(12),
//                 decoration: BoxDecoration(
//                   color: Colors.red.shade100,
//                   borderRadius: BorderRadius.circular(8),
//                   border: Border.all(color: Colors.red.shade300),
//                 ),
//                 child: Column(
//                   crossAxisAlignment: CrossAxisAlignment.start,
//                   children: [
//                     Text(
//                       '⚠️ IMPORTANT',
//                       style: TextStyle(
//                         fontWeight: FontWeight.bold,
//                         color: Colors.red.shade700,
//                       ),
//                     ),
//                     SizedBox(height: 8),
//                     Text(
//                       'If you enable this option:\n\n'
//                       '• The app WILL automatically call your emergency contact when a crisis is detected\n\n'
//                       '• Your contact will see an incoming call from this app\n\n'
//                       '• This cannot be undone after crisis detection starts\n\n'
//                       '• Make sure your contacts have consented to receive emergency calls',
//                       style: TextStyle(fontSize: 12, height: 1.6),
//                     ),
//                   ],
//                 ),
//               ),
//               SizedBox(height: 16),
//               Text(
//                 'I understand the risks and consent to automatic emergency calling',
//                 style: TextStyle(fontSize: 11),
//               ),
//             ],
//           ),
//         ),
//         actions: [
//           TextButton(
//             onPressed: () => Navigator.pop(context),
//             child: Text('CANCEL'),
//           ),
//           ElevatedButton(
//             onPressed: () {
//               settings.autoCallEnabled = true;
//               _emergencyService.updateUserSettings(widget.userId, settings);
//               Navigator.pop(context);
//               _refreshData();

//               ScaffoldMessenger.of(context).showSnackBar(
//                 SnackBar(
//                   content: Text('⚠️ Auto-calling ENABLED'),
//                   backgroundColor: Colors.red.shade600,
//                 ),
//               );
//             },
//             style: ElevatedButton.styleFrom(
//               backgroundColor: Colors.red.shade600,
//             ),
//             child: Text(
//               'I CONSENT - ENABLE AUTO-CALL',
//               style:
//                   TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
//             ),
//           ),
//         ],
//       ),
//     );
//   }
// }
