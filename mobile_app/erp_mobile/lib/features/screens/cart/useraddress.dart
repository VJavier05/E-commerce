import 'package:flutter/material.dart';
import 'package:shewear/utils/constants/colors.dart';
import 'package:shewear/features/screens/cart/addaddress.dart';

class UserAddress extends StatefulWidget {
  const UserAddress({super.key});

  @override
  State<UserAddress> createState() => _UserAddressState();
}

class _UserAddressState extends State<UserAddress> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Addresses'),
        foregroundColor: Colors.white,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Card(
              color: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14),
              ),
              elevation: 3,
              child: ListTile(
                leading: const Icon(Icons.add_location_alt_outlined,
                    color: JColors.primary),
                title: const Text(
                  'Add New Address',
                  style: TextStyle(fontWeight: FontWeight.w500),
                ),
                trailing: const Icon(Icons.chevron_right),
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const AddAddress(),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
