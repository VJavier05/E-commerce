import 'package:flutter/material.dart';
import 'package:shewear/utils/constants/image_strings.dart'; // Assuming JImages is here

class MyOrder extends StatelessWidget {
  const MyOrder({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Orders'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text(
            'Current Orders',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          _OrderCard(
            orderId: '#ORD-20250501',
            status: 'Processing',
            date: 'May 2, 2025',
            total: '₱1,299.00',
            shopName: 'SheWear PH',
            image: JImages.product1,
            title: 'Green Nike sports shoe',
            details: 'Color: Green  Size: EU 34',
            quantity: 1,
          ),
          const SizedBox(height: 16),
          _OrderCard(
            orderId: '#ORD-20250429',
            status: 'Delivered',
            date: 'Apr 29, 2025',
            total: '₱749.00',
            shopName: 'Trend Footwear',
            image: JImages.product2,
            title: 'Pink Adidas Slides',
            details: 'Color: Pink  Size: 37',
            quantity: 2,
          ),
        ],
      ),
    );
  }
}

class _OrderCard extends StatelessWidget {
  final String orderId;
  final String status;
  final String date;
  final String total;
  final String shopName;
  final String image;
  final String title;
  final String details;
  final int quantity;

  const _OrderCard({
    required this.orderId,
    required this.status,
    required this.date,
    required this.total,
    required this.shopName,
    required this.image,
    required this.title,
    required this.details,
    required this.quantity,
  });

  @override
  Widget build(BuildContext context) {
    Color statusColor;

    // Set the status color based on the order status
    switch (status.toLowerCase()) {
      case 'delivered':
        statusColor = Colors.green; // Delivered -> Green
        break;
      case 'processing':
        statusColor = Colors.orange; // Processing -> Orange
        break;
      case 'cancelled':
        statusColor = Colors.red; // Cancelled -> Red
        break;
      default:
        statusColor = Colors.grey; // Default -> Grey
    }

    return Card(
      color: Colors.white, // Set card background to white
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Row to align Shop Name on the left and Status on the right
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                // Shop Name
                Text(shopName,
                    style: const TextStyle(
                        fontSize: 16, fontWeight: FontWeight.bold)),
                // Status
                Text(status,
                    style: TextStyle(
                        color: statusColor,
                        fontWeight: FontWeight.bold,
                        fontSize: 14)),
              ],
            ),
            const SizedBox(height: 8),

            // Product Row
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Product Image
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.asset(
                    image,
                    width: 80,
                    height: 80,
                    fit: BoxFit.cover,
                  ),
                ),
                const SizedBox(width: 12),

                // Product Info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(title,
                          style: const TextStyle(
                              fontWeight: FontWeight.w600, fontSize: 14)),
                      const SizedBox(height: 4),
                      Text(details,
                          style: const TextStyle(
                              color: Colors.grey, fontSize: 13)),
                      const SizedBox(height: 4),
                      Text('Qty: $quantity',
                          style: const TextStyle(fontSize: 13)),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Order ID and Date
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(orderId, style: const TextStyle(color: Colors.grey)),
                Text(date, style: const TextStyle(color: Colors.grey)),
              ],
            ),

            const SizedBox(height: 6),

            const Divider(height: 20),

            // Total
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Total:',
                    style: TextStyle(fontWeight: FontWeight.w500)),
                Text(total,
                    style: const TextStyle(fontWeight: FontWeight.bold)),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
