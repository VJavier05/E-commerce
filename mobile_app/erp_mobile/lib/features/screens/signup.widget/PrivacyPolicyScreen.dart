import 'package:flutter/material.dart';

class PrivacyPolicyScreen extends StatelessWidget {
  const PrivacyPolicyScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Privacy Policy")),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                "Privacy Policy",
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 10),
              const Text(
                "Your privacy is important to us. This policy explains how we handle your data BLAH BLAH BLAH BLAHBLAH BLAHBLAH BLAHBLAH BLAH...",
                style: TextStyle(fontSize: 16),
              ),
              // Add more policy content here
            ],
          ),
        ),
      ),
    );
  }
}
