import 'package:intl/intl.dart';

class JFormatter {
  static String formatDate(DateTime? date) {
    date ??= DateTime.now(); // If date is null, use current date
    return DateFormat('dd-MMM-yyyy').format(date); // Format the date
  }

  static String formatCurrency(double amount) {
    return NumberFormat.currency(locale: 'en_PHP', symbol: '₱')
        .format(amount); // print(formatCurrency(1500)); // Output: "₱1,500.00"
  }

  static String formatPhoneNumber(String phoneNumber) {
    // Remove any non-numeric characters
    phoneNumber = phoneNumber.replaceAll(RegExp(r'\D'), '');

    if (phoneNumber.length == 11 && phoneNumber.startsWith('09')) {
      // Format as 09XX-XXX-XXXX
      return '${phoneNumber.substring(0, 4)}-${phoneNumber.substring(4, 7)}-${phoneNumber.substring(7)}';
    }

    // If not a valid mobile number, return the original input
    return phoneNumber;
  }
}

/*
*
*
* */
