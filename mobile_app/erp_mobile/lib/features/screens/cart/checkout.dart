import 'package:flutter/material.dart';
import 'package:shewear/utils/constants/colors.dart';
import 'package:shewear/utils/constants/image_strings.dart';
import 'package:shewear/features/screens/cart/useraddress.dart';
import 'package:shewear/features/screens/cart/voucher.dart';

class Checkout extends StatelessWidget {
  const Checkout({super.key});

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;

    final products = [
      {
        'image': JImages.product1,
        'title': 'Green Nike sports shoe',
        'details': 'Color Green  Size EU 34',
        'price': 134.0,
        'quantity': 1,
      },
      {
        'image': JImages.product5,
        'title': 'Blue Nike N shoe',
        'details': 'Color Blue  Size EU 34',
        'price': 164.0,
        'quantity': 1,
      },
    ];

    final double subtotal = products.fold(
      0.0,
      (sum, item) => sum + (item['price'] as num),
    );
    final double shipping = 50;
    final double discount = 20;
    final double total = subtotal + shipping - discount;

    return Scaffold(
      backgroundColor: const Color(0xFFF8F8F8),
      appBar: AppBar(
        title: const Text('Checkout'),
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(screenWidth * 0.04),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 1) Address card
            _whiteCard(
              child: ListTile(
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const UserAddress()),
                ),
                leading: const Icon(Icons.location_on, color: JColors.primary),
                title: const Text('John Doe',
                    style: TextStyle(fontWeight: FontWeight.bold)),
                subtitle: const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('123 Main Street, City, Country'),
                    Text('Phone: +1234567890'),
                  ],
                ),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
              ),
            ),
            const SizedBox(height: 6),

            // 2) Products card with shop name header
            _whiteCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Text(
                      'Nike Store',
                      style: TextStyle(
                        fontSize: screenWidth * 0.045,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  ...products.map((product) {
                    return Padding(
                      padding: const EdgeInsets.symmetric(vertical: 6),
                      child: Row(
                        children: [
                          ClipRRect(
                            borderRadius: BorderRadius.circular(12),
                            child: Image.asset(
                              product['image'] as String,
                              width: screenWidth * 0.18,
                              height: screenWidth * 0.18,
                              fit: BoxFit.cover,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(product['title'] as String,
                                    style: TextStyle(
                                        fontWeight: FontWeight.bold,
                                        fontSize: screenWidth * 0.04)),
                                const SizedBox(height: 4),
                                Text(product['details'] as String,
                                    style: TextStyle(
                                        fontSize: screenWidth * 0.035,
                                        color: Colors.grey)),
                              ],
                            ),
                          ),
                          Text(
                            "₱${(product['price'] as num).toStringAsFixed(2)}",
                            style: TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: screenWidth * 0.04),
                          ),
                        ],
                      ),
                    );
                  }).toList(),
                ],
              ),
            ),
            const SizedBox(height: 6),

            // 3) Voucher card (now navigates to Voucher screen)
            _whiteCard(
              child: ListTile(
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const Voucher()),
                  );
                },
                leading: const Icon(Icons.local_offer_outlined,
                    color: JColors.primary),
                title: const Text('Apply Voucher'),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
              ),
            ),
            const SizedBox(height: 6),

            // 4) Payment breakdown
            _whiteCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _paymentRow('Merchandise Subtotal', subtotal, screenWidth),
                  _paymentRow('Shipping Fee', shipping, screenWidth),
                  _paymentRow('Shipping Discount', -discount, screenWidth),
                  const Divider(height: 28),
                  _paymentRow('Total Payment', total, screenWidth,
                      isBold: true),
                ],
              ),
            ),
            const SizedBox(height: 100),
          ],
        ),
      ),

      // 5) Sticky footer
      bottomNavigationBar: Container(
        height: 75,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: const BoxDecoration(
          color: Colors.white,
          boxShadow: [
            BoxShadow(
              color: Color(0x1A000000),
              blurRadius: 6,
              offset: Offset(0, -2),
            ),
          ],
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Total: ₱${total.toStringAsFixed(2)}',
                  style: const TextStyle(
                      fontSize: 16, fontWeight: FontWeight.bold),
                ),
                Text(
                  'Saved Discount: ₱${discount.toStringAsFixed(2)}',
                  style: const TextStyle(
                      fontSize: 14,
                      color: Colors.green,
                      fontWeight: FontWeight.w600),
                ),
              ],
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                padding:
                    const EdgeInsets.symmetric(horizontal: 32, vertical: 12),
                backgroundColor: JColors.primary,
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16)),
              ),
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Order placed successfully!'),
                  ),
                );
              },
              child: const Text("Place Order"),
            ),
          ],
        ),
      ),
    );
  }

  Widget _whiteCard({required Widget child}) => Container(
        margin: const EdgeInsets.only(bottom: 6),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: const [
            BoxShadow(
              color: Color(0x1A000000),
              blurRadius: 6,
              offset: Offset(0, 4),
            ),
          ],
        ),
        child: child,
      );

  Widget _paymentRow(String label, double amount, double screenWidth,
          {bool isBold = false}) =>
      Padding(
        padding: const EdgeInsets.symmetric(vertical: 4),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label,
                style: TextStyle(
                    fontSize: screenWidth * 0.038,
                    fontWeight: isBold ? FontWeight.bold : FontWeight.normal)),
            Text(
              (amount >= 0 ? "₱" : "-₱") + amount.abs().toStringAsFixed(2),
              style: TextStyle(
                fontSize: screenWidth * 0.038,
                fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
                color: JColors.primary,
              ),
            ),
          ],
        ),
      );
}
