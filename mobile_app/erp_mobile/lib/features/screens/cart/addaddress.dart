import 'package:flutter/material.dart';
import 'package:shewear/utils/constants/colors.dart';

class AddAddress extends StatefulWidget {
  const AddAddress({super.key});

  @override
  State<AddAddress> createState() => _AddAddressState();
}

class _AddAddressState extends State<AddAddress> {
  final _formKey = GlobalKey<FormState>();
  final Map<String, String> formData = {
    'fullName': '',
    'contactNumber': '',
    'region': '',
    'province': '',
    'city': '',
    'barangay': '',
    'postalCode': '',
    'streetName': '',
  };

  String selectedLabel = 'Home';
  bool isDefault = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Add New Address"),
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              ...[
                'Full Name',
                'Contact Number',
                'Region',
                'Province',
                'City',
                'Barangay',
                'Postal Code',
                'Street Name',
              ].map((field) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: TextFormField(
                    decoration: InputDecoration(
                      labelText: field,
                      labelStyle: const TextStyle(fontSize: 13.5),
                      filled: true,
                      fillColor: Colors.grey[100],
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    onChanged: (value) =>
                        formData[field.toLowerCase().replaceAll(' ', '')] =
                            value,
                    validator: (value) =>
                        value == null || value.isEmpty ? 'Required' : null,
                  ),
                );
              }).toList(),
              DropdownButtonFormField<String>(
                decoration: InputDecoration(
                  labelText: 'Label',
                  labelStyle: const TextStyle(fontSize: 13.5),
                  filled: true,
                  fillColor: Colors.grey[100],
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                value: selectedLabel,
                items: ['Home', 'Work']
                    .map((label) => DropdownMenuItem(
                          value: label,
                          child: Text(label),
                        ))
                    .toList(),
                onChanged: (value) {
                  setState(() {
                    selectedLabel = value!;
                  });
                },
              ),
              SwitchListTile(
                title: const Text('Set as default address'),
                value: isDefault,
                activeColor: JColors.primary,
                onChanged: (value) {
                  setState(() {
                    isDefault = value;
                  });
                },
              ),
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: JColors.primary,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                    ),
                  ),
                  onPressed: () {
                    if (_formKey.currentState!.validate()) {
                      Navigator.pop(context);
                      // I-save mo dito
                    }
                  },
                  child: const Text(
                    'Submit',
                    style: TextStyle(fontSize: 16),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
