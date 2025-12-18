import 'dart:convert';
import 'package:http/http.dart' as http;
import '../constants/api_constants.dart';

class JHttpHelper {
  static const String _baseUrl = ApiConstants.baseUrl;

  // Generic GET request
  static Future<Map<String, dynamic>> get(String endpoint,
      {Map<String, String>? headers}) async {
    final String url =
        endpoint.startsWith("http") ? endpoint : '$_baseUrl/$endpoint';
    try {
      final response = await http.get(Uri.parse(url), headers: headers);
      return _handleResponse(response);
    } catch (e) {
      return {"error": "Network error: $e"};
    }
  }

  // Generic POST request
  static Future<Map<String, dynamic>> post(String endpoint, dynamic data,
      {Map<String, String>? headers}) async {
    final String url =
        endpoint.startsWith("http") ? endpoint : '$_baseUrl/$endpoint';
    try {
      final response = await http.post(
        Uri.parse(url),
        headers: headers ?? {'Content-Type': 'application/json'},
        body: json.encode(data),
      );
      return _handleResponse(response);
    } catch (e) {
      return {"error": "Network error: $e"};
    }
  }

  // Generic PUT request
  static Future<Map<String, dynamic>> put(String endpoint, dynamic data,
      {Map<String, String>? headers}) async {
    final String url =
        endpoint.startsWith("http") ? endpoint : '$_baseUrl/$endpoint';
    try {
      final response = await http.put(
        Uri.parse(url),
        headers: headers ?? {'Content-Type': 'application/json'},
        body: json.encode(data),
      );
      return _handleResponse(response);
    } catch (e) {
      return {"error": "Network error: $e"};
    }
  }

  // Generic DELETE request
  static Future<Map<String, dynamic>> delete(String endpoint,
      {Map<String, String>? headers}) async {
    final String url =
        endpoint.startsWith("http") ? endpoint : '$_baseUrl/$endpoint';
    try {
      final response = await http.delete(Uri.parse(url), headers: headers);
      return _handleResponse(response);
    } catch (e) {
      return {"error": "Network error: $e"};
    }
  }

  // Improved response handling
  static Map<String, dynamic> _handleResponse(http.Response response) {
    try {
      final Map<String, dynamic> data = json.decode(response.body);

      if (response.statusCode == 200) {
        return data;
      } else if (response.statusCode == 401) {
        return {"message": "Unauthorized: Invalid credentials"};
      } else if (response.statusCode == 403) {
        return {"message": "Forbidden: Access denied"};
      } else if (response.statusCode == 404) {
        return {"message": "Not found: Endpoint does not exist"};
      } else {
        return {
          "message":
              "Error ${response.statusCode}: ${data['message'] ?? 'Something went wrong'}"
        };
      }
    } catch (e) {
      return {"error": "Invalid server response"};
    }
  }
}
