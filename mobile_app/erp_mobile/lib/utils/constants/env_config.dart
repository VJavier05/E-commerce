import 'package:flutter_dotenv/flutter_dotenv.dart';

class EnvConfig {
  static String get apiBaseUrl => dotenv.env['API_BASE_URL'] ?? 'http://127.0.0.1:5000';
  static String get appName => dotenv.env['APP_NAME'] ?? 'SheWear';
  static String get appVersion => dotenv.env['APP_VERSION'] ?? '1.0.0';
  static bool get debugMode => dotenv.env['DEBUG_MODE']?.toLowerCase() == 'true';
  static bool get enableLogging => dotenv.env['ENABLE_LOGGING']?.toLowerCase() == 'true';
}