import 'package:flutter/material.dart';
import 'package:shewear/utils/constants/colors.dart';
import 'package:shewear/common/widgets/appbar/appbar.dart';
import 'package:shewear/features/screens/home/user_home.dart';
import 'package:shewear/features/screens/cart/addtocart.dart';

class UserNotification extends StatelessWidget {
  const UserNotification({super.key});

  @override
  Widget build(BuildContext context) {
    final List<Map<String, String>> notifications = [
      {
        'title': 'Order Shipped',
        'message': 'Your order #12345 has been shipped.',
        'time': '2h ago',
      },
      {
        'title': 'New Message',
        'message': 'You have a new message from Shewear Admin.',
        'time': '5h ago',
      },
      {
        'title': 'Voucher Update',
        'message': 'New 10% discount voucher available!',
        'time': '1 day ago',
      },
    ];

    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 251, 251, 255),
      appBar: JAppBar(
        title: const Text("Notifications"),
        actions: [
          JCountCounterIcon(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const AddToCart()),
              );
            },
            iconColor: JColors.black,
          ),
        ],
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: notifications.length,
        itemBuilder: (context, index) {
          final notification = notifications[index];
          return Container(
            margin: const EdgeInsets.only(bottom: 16),
            decoration: BoxDecoration(
              color: JColors.white,
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: Colors.black12,
                  blurRadius: 6,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: JColors.accent.withOpacity(0.3),
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      Icons.notifications,
                      color: JColors.primary,
                      size: 24,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          notification['title']!,
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: JColors.textPrimary,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          notification['message']!,
                          style: const TextStyle(
                            fontSize: 14,
                            color: JColors.textSecondary,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Row(
                          children: [
                            const Icon(Icons.access_time,
                                size: 14, color: JColors.darkGrey),
                            const SizedBox(width: 4),
                            Text(
                              notification['time']!,
                              style: const TextStyle(
                                fontSize: 12,
                                color: JColors.darkGrey,
                              ),
                            ),
                          ],
                        )
                      ],
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
