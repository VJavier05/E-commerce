import 'package:flutter/material.dart';
import 'package:shewear/utils/constants/colors.dart';
import 'package:shewear/utils/constants/sizes.dart';

class JBottomPlaceOrder extends StatelessWidget {
  final double total;
  final double saved;

  const JBottomPlaceOrder({
    super.key,
    required this.total,
    required this.saved,
  });

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;

    return Container(
      padding: const EdgeInsets.symmetric(
          horizontal: JSizes.defaultSpace, vertical: JSizes.defaultSpace / 2),
      decoration: BoxDecoration(
        color: dark ? JColors.darkGrey : JColors.light,
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(JSizes.cardRadiusLg),
          topRight: Radius.circular(JSizes.cardRadiusLg),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _bottomTextRow("Total:", total),
              _bottomTextRow("Saved:", saved),
            ],
          ),
          ElevatedButton(
            onPressed: () {},
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.all(JSizes.md),
              backgroundColor: JColors.black,
              side: const BorderSide(color: JColors.black),
            ),
            child: const Text("Place Order"),
          ),
        ],
      ),
    );
  }

  Widget _bottomTextRow(String label, double amount) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Text(
            label,
            style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: JColors.primary),
          ),
          const SizedBox(width: 8),
          Text(
            "₱${amount.toStringAsFixed(2)}",
            style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: amount > 0 ? Colors.green : Colors.red),
          ),
        ],
      ),
    );
  }
}
