import 'package:logger/logger.dart';

// FOR DEBUGGING
class JLoggerHelper {
  static final Logger _logger = Logger(
    printer: PrettyPrinter(), // Printer that formats logs in a readable way
    level: Level.debug, // Sets the minimum log level to 'debug'
  );

  static void debug(String message) {
    _logger.d(message);
  }

  static void info(String message) {
    _logger.i(message);
  }

  static void warning(String message) {
    _logger.w(message);
  }

  static void error(String message, [dynamic error]) {
    _logger.e(message, error: error, stackTrace: StackTrace.current);
  }
}
