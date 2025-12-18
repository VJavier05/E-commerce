import 'dart:convert';
import 'package:shewear/utils/constants/api_constants.dart';
import 'package:http/http.dart' as http;

class ApiService {
  // Function to test connection
  static Future<String> testConnection() async {
    final response = await http.get(Uri.parse(ApiConstants.testEndpoint));

    if (response.statusCode == 200) {
      var data = json.decode(response.body);
      return data["message"];
    } else {
      throw Exception("Failed to connect to Flask");
    }
  }
}
