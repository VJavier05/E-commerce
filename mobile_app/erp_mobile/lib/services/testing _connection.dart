import 'package:flutter/material.dart';

import '../utils/constants/api_constants.dart';
import '../utils/http/http_client.dart';

class TestConnectionScreen extends StatefulWidget {
  const TestConnectionScreen({super.key});

  @override
  _TestConnectionScreenState createState() => _TestConnectionScreenState();
}

class _TestConnectionScreenState extends State<TestConnectionScreen> {
  String _connectionMessage = "Click the button to test connection";

  Future<void> _checkConnection() async {
    try {
      // Use JHttpHelper to make a GET request
      final response = await JHttpHelper.get(ApiConstants.testEndpoint);

      setState(() {
        _connectionMessage = response["message"]; // Display Flask response
      });
    } catch (e) {
      setState(() {
        _connectionMessage = "Failed to connect: $e";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Test Flask Connection")),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              _connectionMessage,
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _checkConnection,
              child: Text("Test Connection"),
            ),
          ],
        ),
      ),
    );
  }
}
