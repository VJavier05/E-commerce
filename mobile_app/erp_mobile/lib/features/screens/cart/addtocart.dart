import 'package:flutter/material.dart';
import 'package:shewear/utils/constants/colors.dart';
import 'package:shewear/utils/constants/image_strings.dart';
import 'package:iconsax/iconsax.dart';
import 'package:shewear/features/screens/message/userchat.dart';
import 'package:shewear/features/screens/cart/checkout.dart';

class AddToCart extends StatefulWidget {
  const AddToCart({super.key});

  @override
  State<AddToCart> createState() => _AddToCartState();
}

class _AddToCartState extends State<AddToCart> {
  final Map<String, List<Map<String, dynamic>>> groupedCartItems = {
    'Nike Store': [
      {
        'image': JImages.product1,
        'title': 'Green Nike sports shoe',
        'details': 'Color Green  Size EU 34',
        'price': 134.0,
        'quantity': 1,
        'selected': true,
      },
      {
        'image': JImages.product5,
        'title': 'Green N shoe',
        'details': 'Color blue  Size EU 34',
        'price': 164.0,
        'quantity': 1,
        'selected': true,
      },
    ],
    'ZARA Shop': [
      {
        'image': JImages.product2,
        'title': 'Blue T-shirt for all ages',
        'details': '',
        'price': 35.0,
        'quantity': 1,
        'selected': true,
      },
    ],
    'Apple Hub': [
      {
        'image': JImages.product3,
        'title': 'iPhone 14 Pro 512 GB',
        'details': '',
        'price': 1998.0,
        'quantity': 2,
        'selected': false,
      },
    ],
  };

  double get total {
    double sum = 0;
    for (var shop in groupedCartItems.values) {
      for (var item in shop) {
        if (item['selected']) {
          sum += item['price'] * item['quantity'];
        }
      }
    }
    return sum;
  }

  void _removeItem(String shopName, Map<String, dynamic> item) {
    setState(() {
      groupedCartItems[shopName]?.remove(item);
      if (groupedCartItems[shopName]?.isEmpty ?? true) {
        groupedCartItems.remove(shopName);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      backgroundColor: isDark ? Colors.black : Colors.white,
      appBar: AppBar(
        backgroundColor: isDark ? Colors.black : Colors.white,
        elevation: 0,
        title: Text(
          'Cart',
          style: TextStyle(
            color: isDark ? Colors.white : Colors.black,
            fontWeight: FontWeight.bold,
          ),
        ),
        iconTheme: IconThemeData(color: isDark ? Colors.white : Colors.black),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: IconButton(
              icon: Icon(Iconsax.message, color: JColors.black),
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const UserChat()),
                );
              },
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: groupedCartItems.entries.map((entry) {
                final shopName = entry.key;
                final items = entry.value;

                return Card(
                  color: Colors.white, // Set card background to white
                  margin: const EdgeInsets.only(
                      bottom: 10), // Reduced from 20 to 10
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16)),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          shopName,
                          style: const TextStyle(
                              fontWeight: FontWeight.bold, fontSize: 16),
                        ),
                        const SizedBox(height: 12),
                        ...items.map((item) {
                          return Dismissible(
                            key: Key(item['title']),
                            direction: DismissDirection.endToStart,
                            onDismissed: (direction) {
                              _removeItem(shopName, item);
                            },
                            background: Container(
                              color: Colors.red,
                              alignment: Alignment.centerRight,
                              padding:
                                  const EdgeInsets.symmetric(horizontal: 20),
                              child:
                                  const Icon(Icons.delete, color: Colors.white),
                            ),
                            child: Container(
                              margin: const EdgeInsets.only(bottom: 12),
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.center,
                                children: [
                                  Checkbox(
                                    value: item['selected'],
                                    onChanged: (value) {
                                      setState(() {
                                        item['selected'] = value!;
                                      });
                                    },
                                    activeColor: JColors.primary,
                                  ),
                                  ClipRRect(
                                    borderRadius: BorderRadius.circular(8),
                                    child: Image.asset(
                                      item['image'],
                                      width: 48,
                                      height: 48,
                                      fit: BoxFit.cover,
                                    ),
                                  ),
                                  const SizedBox(width: 10),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          item['title'],
                                          style: const TextStyle(
                                              fontWeight: FontWeight.bold),
                                        ),
                                        if (item['details'] != '')
                                          Text(
                                            item['details'],
                                            style:
                                                const TextStyle(fontSize: 12),
                                          ),
                                        const SizedBox(height: 4),
                                        Row(
                                          mainAxisAlignment:
                                              MainAxisAlignment.spaceBetween,
                                          children: [
                                            Row(
                                              children: [
                                                IconButton(
                                                  onPressed: () {
                                                    setState(() {
                                                      if (item['quantity'] >
                                                          1) {
                                                        item['quantity']--;
                                                      }
                                                    });
                                                  },
                                                  icon: Icon(
                                                    Icons.remove_circle_outline,
                                                    color: JColors.primary,
                                                  ),
                                                  padding: EdgeInsets.zero,
                                                  constraints:
                                                      const BoxConstraints(),
                                                ),
                                                Padding(
                                                  padding: const EdgeInsets
                                                      .symmetric(horizontal: 6),
                                                  child: Text(
                                                      item['quantity']
                                                          .toString(),
                                                      style: const TextStyle(
                                                          fontSize: 14)),
                                                ),
                                                IconButton(
                                                  onPressed: () {
                                                    setState(() {
                                                      item['quantity']++;
                                                    });
                                                  },
                                                  icon: Icon(
                                                    Icons.add_circle_outline,
                                                    color: JColors.primary,
                                                  ),
                                                  padding: EdgeInsets.zero,
                                                  constraints:
                                                      const BoxConstraints(),
                                                ),
                                              ],
                                            ),
                                            Text(
                                              '₱${(item['price'] * item['quantity']).toStringAsFixed(2)}',
                                              style: const TextStyle(
                                                  fontWeight: FontWeight.bold),
                                            ),
                                          ],
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          );
                        }).toList(),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
            decoration: BoxDecoration(
              color: isDark
                  ? Colors.grey[850]
                  : const Color.fromARGB(255, 255, 255, 255),
              boxShadow: const [
                BoxShadow(color: Colors.black12, blurRadius: 12)
              ],
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Total: ₱${total.toStringAsFixed(2)}',
                  style: const TextStyle(
                      fontSize: 16, fontWeight: FontWeight.bold),
                ),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 32, vertical: 12),
                    backgroundColor: JColors.primary,
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16)),
                  ),
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => const Checkout()),
                    );
                  },
                  child: const Text("Checkout"),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
