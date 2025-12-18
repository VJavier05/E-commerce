import '../constants/env_config.dart';

class ApiConstants {
  static String get baseUrl => EnvConfig.apiBaseUrl;

  // Endpoints
  static String get testEndpoint => "$baseUrl/test";

  // Authentication Endpoints
  static String get login => "$baseUrl/api/login";
  static String get register => "$baseUrl/api/register";
  static String get protected => "$baseUrl/api/protected";

  // Orders
  static String get getOrders => "$baseUrl/api/orders";
  static String get placeOrder => "$baseUrl/api/place-order";

  // Add more as needed
  // static const String userProfile = "$baseUrl/api/profile";
  // static const String updateProfile = "$baseUrl/api/update-profile";
}
