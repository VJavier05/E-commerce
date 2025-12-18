import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';
import 'package:shewear/common/widgets/appbar/appbar.dart';
import 'package:shewear/common/widgets/text/section_header.dart';
import 'package:shewear/common/widgets/setting/setting_tile.dart';
import 'package:shewear/common/widgets/setting/user_profile_tile.dart';
import 'package:shewear/features/screens/cart/useraddress.dart';
import 'package:shewear/features/screens/cart/addtocart.dart';
import 'package:shewear/features/screens/cart/voucher.dart';
import 'package:shewear/features/screens/cart/myorder.dart';
import 'package:shewear/utils/constants/colors.dart';
import 'package:shewear/utils/constants/sizes.dart';
import 'package:shewear/features/screens/home/user_home.dart';

class SettingScreen extends StatelessWidget {
  const SettingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Header
            JPrimaryHeaderContainer(
              child: Column(
                children: [
                  JAppBar(
                    title: Text(
                      "Account",
                      style: Theme.of(context)
                          .textTheme
                          .headlineMedium!
                          .apply(color: JColors.white),
                    ),
                  ),
                  const JUserProfile(),
                  const SizedBox(height: JSizes.spaceBtwSections),
                ],
              ),
            ),

            // Body
            Padding(
              padding: const EdgeInsets.all(JSizes.defaultSpace),
              child: Column(
                children: [
                  const JSectionHeading(title: "Account Setting"),
                  const SizedBox(height: JSizes.spaceBtwItems),

                  // My Addresses
                  JSettingMenuTile(
                    icon: Iconsax.safe_home,
                    title: "My Addresses",
                    subtitle: "Set Address",
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                            builder: (context) => const UserAddress()),
                      );
                    },
                  ),

                  // My Cart
                  JSettingMenuTile(
                    icon: CupertinoIcons.shopping_cart,
                    title: "My Cart",
                    subtitle: "Add, Remove Products",
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                            builder: (context) => const AddToCart()),
                      );
                    },
                  ),

                  // My Orders
                  JSettingMenuTile(
                    icon: Iconsax.bag_tick,
                    title: "My Orders",
                    subtitle: "Monitor Orders",
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                            builder: (context) => const MyOrder()),
                      );
                    },
                  ),

                  // My Coupons
                  JSettingMenuTile(
                    icon: Iconsax.discount_shape,
                    title: "My Coupons",
                    subtitle: "List of discounted Coupons",
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                            builder: (context) => const Voucher()),
                      );
                    },
                  ),

                  const SizedBox(height: JSizes.spaceBtwSections),

                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton(
                      onPressed: () {
                        // TODO: Logout logic
                      },
                      child: const Text("Logout"),
                    ),
                  ),

                  const SizedBox(height: JSizes.spaceBtwSections * 2.5),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
